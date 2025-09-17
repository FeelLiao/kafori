from fastapi import APIRouter, UploadFile, File, Depends, Request
from typing import Tuple
import logging
from io import BytesIO
from typing import Annotated
from pathlib import Path
import aiofiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from backend.api.files import UploadFileProcessor, FileType, GeneDataType, PutDataBaseWrapper, UpstreamAnalysisWrapper
from backend.routers.validation import get_current_active_user, User
from backend.db.result.Result import Result
from backend.db.interface import PutDataBaseInterface
from backend.api.config import config

import os, hashlib, shutil
import aiofiles
from fastapi import Form


file_router = APIRouter()
logger = logging.getLogger(__name__)
UPLOAD_RAWDATA_PATH = Path(config.upload_rawdata_dir)
REF_GENOME = Path(config.ref_genome)
REF_ANNOTATION = Path(config.ref_annotation)
UPSTREAM_CORES = int(config.upstream_cores)
Redis_expires = 600  # seconds
EXECUTOR = ThreadPoolExecutor(max_workers=2)


async def sample_sheet_validation(file: BytesIO, user: str, name: str, request: Request) -> Tuple[bool, str]:
    """
    Process the uploaded file.
    Args:
        file (BytesIO): The uploaded file in memory.
    Returns:
        Tuple[bool, str]: A tuple containing a success flag and a message.
    """
    try:
        redis = request.app.state.redis
        sample_sheet_data = UploadFileProcessor.read_file(
            file, file_type=FileType.xlsx)
        valid = UploadFileProcessor.sample_data_validation(
            name, sample_sheet_data)
        if valid:

            logger.info(
                f"Sample sheet data is valid for user {user}, saving to redis.")

            sample_save = sample_sheet_data.to_parquet()
            await redis.set(f"{user}_sample_sheet", sample_save, ex=Redis_expires)
            logger.info(
                f"Sample sheet for user {user} saved to redis successfully.")
            return valid, "Sample sheet uploaded successfully."
        else:
            return False, "Sample sheet uploaded failed."
    except Exception as e:
        return False, str(e)


async def process_gene_ex(file: BytesIO | pd.DataFrame, user: str, name: str,
                          request: Request | None, type: GeneDataType, redis=None) -> Tuple[bool, str]:
    """
    Process the uploaded gene expression file.
    Args:
        file (BytesIO): The uploaded file in memory.
    Returns:
        Tuple[bool, str]: A tuple containing a success flag and a message.
    """
    try:
        if redis is None:
            assert request is not None, "request is required when redis is None"
            redis = request.app.state.redis

        if isinstance(file, pd.DataFrame):
            gene_tpm_data = file
        else:
            gene_tpm_data = UploadFileProcessor.read_file(
                file, file_type=FileType.csv)

        logger.info(f"{name} file read successfully for user {user}.")

        sample_sheet = BytesIO(await redis.get(f"{user}_sample_sheet"))

        logger.info(
            f"sample sheet recovered from redis for user {user} successfully.")

        sample_sheet_data = UploadFileProcessor.read_file(
            sample_sheet, file_type=FileType.parquet)

        logger.info(
            f"sample sheet data read successfully for user {user} in gene expression process.")

        valid = UploadFileProcessor.gene_ex_validation(
            sample_sheet_data, gene_tpm_data)
        if valid:
            gene_save = gene_tpm_data.to_parquet()
            await redis.set(f"{user}_gene_{type}", gene_save, ex=Redis_expires)
            logger.info(
                f"Gene expression data {type}_{name} for user {user} saved to redis successfully.")
        return valid, f"Gene expression data {type}_{name} uploaded successfully."
    except Exception as e:
        return False, str(e)


# 是否需要在redis中存储用户选择的上传类别，然后在后续处理时使用？
async def process_db_upload(user: str, request: Request) -> Tuple[bool, str]:
    try:
        redis = request.app.state.redis
        sample_sheet = BytesIO(await redis.get(f"{user}_sample_sheet"))
        sample_sheet_data = UploadFileProcessor.read_file(
            sample_sheet, file_type=FileType.parquet)
        logger.info(
            f"sample sheet file extracted successfully for user {user}.")
        gene_tpm = BytesIO(await redis.get(f"{user}_gene_{GeneDataType.tpm}"))
        gene_tpm_data = UploadFileProcessor.read_file(
            gene_tpm, file_type=FileType.parquet)
        logger.info(f"gene tpm file extracted successfully for user {user}.")
        gene_counts = BytesIO(await redis.get(f"{user}_gene_{GeneDataType.counts}"))
        gene_counts_data = UploadFileProcessor.read_file(
            gene_counts, file_type=FileType.parquet)
        logger.info(
            f"gene counts file extracted successfully for user {user}.")

        data_base_wrapper = PutDataBaseWrapper(
            sample_sheet_data, gene_tpm_data, gene_counts_data)
        exp_class_communication = data_base_wrapper.communicate_id_in_db()
        exp_class_communication_r = await PutDataBaseInterface.exclass_processing(exp_class_communication)
        logger.info(
            f"Experiment class has put into database successfully for user {user}.")

        exp_sheet, sample_sheet = data_base_wrapper.db_insert(
            exp_class_communication_r)
        tpm, counts = data_base_wrapper.expression_wrapper(sample_sheet)

        exp_valid = await PutDataBaseInterface.put_experiment(exp_sheet)
        if exp_valid:
            logger.info(
                f"Experiment data has been put into database successfully for user {user}.")
        sample_valid = await PutDataBaseInterface.put_sample(sample_sheet)
        sample_sheet.to_csv(f"{user}_sample_sheet.csv", index=False)
        if sample_valid:
            logger.info(
                f"Sample data has been put into database successfully for user {user}.")
        tpm_valid = await PutDataBaseInterface.put_gene_tpm(tpm)
        if tpm_valid:
            logger.info(
                f"Gene TPM data has been put into database successfully for user {user}.")
        counts_valid = await PutDataBaseInterface.put_gene_counts(counts)
        if counts_valid:
            logger.info(
                f"Gene Counts data has been put into database successfully for user {user}.")

        valid = [exp_valid, sample_valid, tpm_valid, counts_valid]
        if all(valid):
            return True, "Database data uploaded successfully."
        else:
            return False, "Database data upload failed. Please see log for more information"
    except Exception as e:
        logger.error(
            f"Error in putting data into database for user {user}: {e}", exc_info=True)
        return False, str(e)


async def upload_file_saving(file: UploadFile, save_path: Path) -> None:
    save_path = Path(save_path, file.filename)

    async with aiofiles.open(save_path,  "wb") as f:
        while chunk := await file.read(8192):
            await f.write(chunk)


def _run_upstream_job(user: str,
                      analysis: UpstreamAnalysisWrapper,
                      cores: int,
                      redis,
                      loop: asyncio.AbstractEventLoop):
    # 在线程中将异步 Redis 操作提交回主事件循环
    def set_status(val: str):
        fut = asyncio.run_coroutine_threadsafe(
            redis.set(f"{user}_upstream_status", val), loop
        )
        try:
            fut.result()
        except Exception:
            logger.error("Failed to update upstream status")

    set_status("running")
    try:
        ok = analysis.smk_run(cores)
        if not ok:
            set_status("error")
            return
        logger.info(
            f"Upstream analysis workflow {('finished' if ok else 'failed')} for user {user}.")
        logger.info(
            "Starting post-processing. This may take some time. Please wait...")
        res = analysis.post_process()
        tpm = res["quantification"][0]
        counts = res["quantification"][1]
        fut_tpm = asyncio.run_coroutine_threadsafe(
            process_gene_ex(tpm, user, "tpm_from_pipeline",
                            request=None, type=GeneDataType.tpm, redis=redis),
            loop
        )
        fut_counts = asyncio.run_coroutine_threadsafe(
            process_gene_ex(counts, user, "counts_from_pipeline",
                            request=None, type=GeneDataType.counts, redis=redis),
            loop
        )
        ok_tpm, msg_tpm = fut_tpm.result()
        ok_counts, msg_counts = fut_counts.result()
        if not ok_tpm or not ok_counts:
            logger.error(
                f"Saving gene data failed: tpm={ok_tpm}:{msg_tpm}, counts={ok_counts}:{msg_counts}")

        align_status = res["align_report"][0]
        align_report = res["align_report"][1]
        fastp_status = res["fastp_report"][0]
        fastp_report = res["fastp_report"][1]

        if align_status:
            async def save_align():
                _save = align_report.to_parquet()
                await redis.set(f"{user}_align_reports", _save, ex=Redis_expires)
            asyncio.run_coroutine_threadsafe(save_align(), loop)
            logger.info(
                f"Alignment report for user {user} saved to redis successfully.")
        else:
            logger.error(
                f"Alignment report generation failed for user {user}.")
        if fastp_status:
            async def save_fastp():
                _save = fastp_report.to_parquet()
                await redis.set(f"{user}_fastp_reports", _save, ex=Redis_expires)
            asyncio.run_coroutine_threadsafe(save_fastp(), loop)
            logger.info(
                f"Fastp report for user {user} saved to redis successfully.")
        else:
            logger.error(f"Fastp report generation failed for user {user}.")

        set_status("finished")
    except Exception as e:
        set_status(f"error:{e}")


async def run_upstream(user: str, request: Request) -> Tuple[bool, str]:
    try:
        redis = request.app.state.redis
        sample_sheet = BytesIO(await redis.get(f"{user}_sample_sheet"))
        sample_sheet_data = UploadFileProcessor.read_file(
            sample_sheet, file_type=FileType.parquet)
        logger.info(
            f"sample sheet file extracted successfully for user {user} in upstream process.")
        rawdata_path = Path(UPLOAD_RAWDATA_PATH, user, "rawdata")
        work_dir = Path(UPLOAD_RAWDATA_PATH, user)
        analysis = UpstreamAnalysisWrapper(user=user,
                                           work_dir=work_dir, rawdata_dir=rawdata_path,
                                           sample_sheet=sample_sheet_data,
                                           genome=REF_GENOME, annotation=REF_ANNOTATION)

        await redis.set(f"{user}_upstream_status", "pending")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(EXECUTOR, analysis.smk_dry_run)
        if result:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(
                EXECUTOR,
                _run_upstream_job,
                user, analysis, UPSTREAM_CORES, redis, loop
            )
            logger.info(
                f"Upstream analysis workflow started successfully for user {user}.")
            return True, "Dry run passed. Upstream analysis is running in background."
        else:
            await redis.set(f"{user}_upstream_status", "failed:dry_run")
            return False, "Dry run failed. Please see log for more information."
    except Exception as e:
        logger.error(
            f"Error in running upstream analysis for user {user}: {e}", exc_info=True)
        return False, str(e)


@file_router.post("/pipeline/sample_sheet/")
async def upload_sample_sheet(request: Request,
                              current_user: Annotated[User, Depends(get_current_active_user)],
                              file: UploadFile = File(...,
                                                      description="Upload sample sheet file"),
                              ):
    user = current_user.username
    sample_sheet_name = file.filename
    sample_sheet_io = BytesIO(await file.read())
    rel = await sample_sheet_validation(
        sample_sheet_io, user=user, name=sample_sheet_name, request=request)
    if rel[0]:
        return Result.ok(msg=rel[1])
    else:
        return Result.fail(msg=rel[1])


@file_router.post("/pipeline/gene_ex_tpm/")
async def upload_gene_ex_tpm(request: Request,
                             current_user: Annotated[User, Depends(get_current_active_user)],
                             file: UploadFile = File(...,
                                                     description="Upload gene expression file standard by tpm method")):
    user = current_user.username
    gene_tpm_name = file.filename
    gene_tpm = BytesIO(await file.read())
    rel = await process_gene_ex(
        gene_tpm, user=user, name=gene_tpm_name,
        request=request, type=GeneDataType.tpm)
    if rel[0]:
        return Result.ok(msg=rel[1])
    else:
        return Result.fail(msg=rel[1])


@file_router.post("/pipeline/gene_ex_counts/")
async def upload_gene_ex_counts(request: Request,
                                current_user: Annotated[User, Depends(get_current_active_user)],
                                file: UploadFile = File(...,
                                                        description="Upload gene expression file standard by "
                                                        "counts method")):
    user = current_user.username
    gene_counts_name = file.filename
    gene_counts = BytesIO(await file.read())
    rel = await process_gene_ex(
        gene_counts, user=user, name=gene_counts_name,
        request=request, type=GeneDataType.counts)
    if rel[0]:
        return Result.ok(msg=rel[1])
    else:
        return Result.fail(msg=rel[1])


# 上传rawdata，将上传的数据存储在本地 upload_rawdata_dir/<user>/file.fastq,
# 上传完成后利用样本信息表对rawdata的文件进行md5校验，然后返回检验结果给前端
@file_router.post("/pipeline/rawdata_upload/")
async def upload_rawdata(current_user: Annotated[User, Depends(get_current_active_user)],
                         files: list[UploadFile] = File(
    description="Multiple rawdata files Upload"),
):
    pass


# 对rawdata进行转录组上游分析，发送信号过后返回是否成功启动了上游分析流程
@file_router.post("/pipeline/rawdata_processing/")
async def process_rawdata(current_user: Annotated[User, Depends(get_current_active_user)],
                          request: Request):
    user = current_user.username
    rel = await run_upstream(user=user, request=request)
    if rel[0]:
        return Result.ok(msg=rel[1])
    else:
        return Result.fail(msg=rel[1])


# 返回rawdata处理状态
@file_router.post("/pipeline/rawdata_status/")
async def get_rawdata_status(current_user: Annotated[User, Depends(get_current_active_user)],
                             request: Request):
    user = current_user.username
    redis = request.app.state.redis
    status = await redis.get(f"{user}_upstream_status")
    if isinstance(status, (bytes, bytearray)):
        status = status.decode()
    return Result.ok(data={"status": status or "unknown"}, msg="OK")


@file_router.post("/pipeline/rawdata_results/")
async def get_rawdata_results(current_user: Annotated[User, Depends(get_current_active_user)],
                              request: Request):
    user = current_user.username
    redis = request.app.state.redis
    finished = await redis.get(f"{user}_upstream_status")
    if isinstance(finished, (bytes, bytearray)):
        finished = finished.decode()
    if finished != "finished":
        return Result.fail(msg="Upstream analysis not finished yet.")
    else:
        align_reports = UploadFileProcessor.read_file(BytesIO(await redis.get(f"{user}_align_reports")),
                                                      file_type=FileType.parquet)
        fastp_reports = UploadFileProcessor.read_file(BytesIO(await redis.get(f"{user}_fastp_reports")),
                                                      file_type=FileType.parquet)
        results = {
            "align_reports": align_reports.to_dict(orient="records"),
            "fastp_reports": fastp_reports.to_dict(orient="records"),
        }
        return Result.ok(data=results, msg="Upstream analysis results retrieved successfully.")


@file_router.post("/pipeline/put_database/")
async def put_database(request: Request,
                       current_user: Annotated[User, Depends(get_current_active_user)],
                       ):
    user = current_user.username
    rel = await process_db_upload(user=user, request=request)
    if rel[0]:
        return Result.ok(msg=rel[1])
    else:
        return Result.fail(msg=rel[1])







@file_router.post("/upload_chunk/")
async def upload_chunk(
        request: Request,
        file: UploadFile,
        index: int = Form(...),
        total_chunks: int = Form(...)
):
    user = "admin"
    redis = request.app.state.redis

    os.makedirs(f"{UPLOAD_RAWDATA_PATH}/{user}", exist_ok=True)
    chunk_path = f"{UPLOAD_RAWDATA_PATH}/{user}/{index}"
    content = await file.read()
    async with aiofiles.open(chunk_path, "wb") as f:
        await f.write(content)
    # 只在最后一个分片时统计
    await redis.sadd(f"upload:{user}", index)
    uploaded = await redis.scard(f"upload:{user}")
    if uploaded == total_chunks:
        final_path = f"{UPLOAD_RAWDATA_PATH}/{user}.final"
        await merge_chunks_parallel_async(user, total_chunks, final_path)
        shutil.rmtree(f"{UPLOAD_RAWDATA_PATH}/{user}")
        await redis.delete(f"upload:{user}")
        return {"code": 0, "msg": "上传成功，文件已合并"}
    return {"code": 0, "msg": "分片上传成功"}

# filepath: /home/zhoujunjie/kafori/backend/routers/file_routers.py
async def merge_chunks_parallel_async(user, total_chunks, final_path):
    chunk_dir = f"{UPLOAD_RAWDATA_PATH}/{user}"
    async with aiofiles.open(final_path, "wb") as f:
        for i in range(total_chunks):
            chunk_path = os.path.join(chunk_dir, str(i))
            async with aiofiles.open(chunk_path, "rb") as chunk_f:
                while True:
                    data = await chunk_f.read(8 * 1024 * 1024)
                    if not data:
                        break
                    await f.write(data)

