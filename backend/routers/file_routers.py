from __future__ import annotations
import errno
from fastapi import (APIRouter,
                     UploadFile, File, Depends, Request, Body,
                     Header)
from typing import Tuple, Optional
import logging
from io import BytesIO
from typing import Annotated
from pathlib import Path
import aiofiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
import pandas as pd
import contextlib
import os
import json

from pydantic import BaseModel
try:
    from starlette.requests import ClientDisconnect
except Exception:
    from starlette.exceptions import ClientDisconnect

from backend.api.files import UploadFileProcessor, FileType, GeneDataType, PutDataBaseWrapper, UpstreamAnalysisWrapper
from backend.routers.validation import get_current_active_user, User
from backend.db.result.Result import Result
from backend.db.interface import PutDataBaseInterface
from backend.api.config import config


file_router = APIRouter()
logger = logging.getLogger(__name__)

# upstream settings
REF_GENOME = Path(config.upstream.ref_genome)
REF_ANNOTATION = Path(config.upstream.ref_annotation)
UPSTREAM_CORES = int(config.upstream.upstream_cores)
EXECUTOR = ThreadPoolExecutor(max_workers=2)

# redis settings
Redis_expires = int(config.redis_timeout)  # seconds

# rawdata upload path
UPLOAD_RAWDATA_PATH = Path(config.upstream.upload_rawdata_dir).resolve()
UPLOAD_RAWDATA_PATH.mkdir(parents=True, exist_ok=True)
# 可选：设置一个最大体积（字节），超过则拒绝
MAX_BYTES: Optional[int] = None  # 例如 10 * 1024**3  # 10 GiB


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
            files_md5 = UploadFileProcessor.sample_file_md5(sample_sheet_data)
            await redis.set(f"{user}_files_md5", json.dumps(files_md5), ex=Redis_expires)
            logger.info(
                f"files_md5 for user {user} saved to redis successfully.")
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
        gene_tpm_data = UploadFileProcessor.read_file_v2(gene_tpm)
        logger.info(f"gene tpm file extracted successfully for user {user}.")
        gene_counts = BytesIO(await redis.get(f"{user}_gene_{GeneDataType.counts}"))
        gene_counts_data = UploadFileProcessor.read_file_v2(gene_counts)
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
        expression = data_base_wrapper.expression_wrapper_v2(sample_sheet)

        exp_valid = await PutDataBaseInterface.put_experiment(exp_sheet)
        if exp_valid:
            logger.info(
                f"Experiment data has been put into database successfully for user {user}.")
        sample_valid = await PutDataBaseInterface.put_sample(sample_sheet)
        if sample_valid:
            logger.info(
                f"Sample data has been put into database successfully for user {user}.")

        expression_valid = await PutDataBaseInterface.put_expression_v2(expression)
        if expression_valid:
            logger.info(
                f"Gene Expression data has been put into database successfully for user {user}.")

        valid = [exp_valid, sample_valid, expression_valid]
        if all(valid):
            return True, "Database data uploaded successfully."
        else:
            return False, "Database data upload failed. Please see log for more information"
    except Exception as e:
        logger.error(
            f"Error in putting data into database for user {user}: {e}", exc_info=True)
        return False, str(e)


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


def safe_target_path(UPLOAD_DIR: Path, filename: str) -> Path:
    filename = Path(filename).name.strip().replace("\x00", "")
    target = (UPLOAD_DIR / filename).resolve()
    # 防止路径穿越
    # Python 3.9+ 可用 is_relative_to
    if not target.is_relative_to(UPLOAD_DIR):
        raise Exception(f"Invalid filename/path: {filename}")
    return target


async def upload_files(target: Path, request: Request, content_length: Optional[int] = None) -> Tuple[str, int]:
    tmp = target.with_suffix(target.suffix + ".part")
    tmp.parent.mkdir(parents=True, exist_ok=True)

    total = 0

    try:
        async with aiofiles.open(tmp, "wb") as f:
            logger.info(f"Start uploading to temporary file: {tmp}")
            async for chunk in request.stream():
                if not chunk:
                    continue
                total += len(chunk)
                if MAX_BYTES is not None and total > MAX_BYTES:
                    raise Exception(f"file is too large: {target.name}")
                await f.write(chunk)

        logger.info(f"Finished uploading to temporary file: {tmp}")

        if content_length is not None and total != int(content_length):
            with contextlib.suppress(Exception):
                tmp.unlink()
            raise Exception(
                f"Content-Length mismatch: got={total}, expected={content_length}")
        # 原子落盘：优先硬链接，不覆盖已存在；必要时回退 replace（同分区原子）
        try:
            os.link(tmp, target)  # 若目标已存在会抛 FileExistsError
        except FileExistsError:
            with contextlib.suppress(Exception):
                tmp.unlink()
            raise Exception(f"Target file already exists: {target.name}")
        except OSError as e:
            # 跨分区/权限不足等，回退到 replace，仍不覆盖既有文件
            if e.errno in (errno.EXDEV, errno.EPERM, errno.EACCES):
                if target.exists():
                    with contextlib.suppress(Exception):
                        tmp.unlink()
                    raise Exception(
                        f"Target file already exists: {target.name}")
                tmp.replace(target)  # pathlib 原子替换
            else:
                with contextlib.suppress(Exception):
                    tmp.unlink()
                raise
        finally:
            with contextlib.suppress(Exception):
                if tmp.exists():
                    tmp.unlink()
        logger.info(f"File saved successfully: {target.name}")
        return target.name, total
    except ClientDisconnect:
        with contextlib.suppress(Exception):
            if tmp.exists():
                tmp.unlink()
        raise
    except Exception:
        # 发生异常时尽量清理残留
        with contextlib.suppress(Exception):
            if tmp.exists():
                tmp.unlink()
        raise


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


@file_router.put("/pipeline/rawdata_upload")
async def rawdata_upload(
    request: Request,
    # 元数据可从查询参数传递
    filename: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    # 可选：让客户端传 content length 与哈希方便校验
    content_length: Optional[int] = Header(
        default=None, alias="Content-Length")
):
    """
    原始流上传：客户端以 application/octet-stream 直传请求体。
    例：curl -T bigfile.bin "http://localhost:8000/upload?filename=bigfile.bin" -H 
    "Content-Type: application/octet-stream"
    """
    if request.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/octet-stream":
        logger.warning(
            "Invalid Content-Type, Content-Type must be application/octet-stream")
        return Result.fail(
            msg="Content-Type must be application/octet-stream")

    user = current_user.username
    rawdata_path = Path(UPLOAD_RAWDATA_PATH, user, "rawdata").resolve()
    rawdata_path.mkdir(parents=True, exist_ok=True)
    try:
        target = safe_target_path(rawdata_path, filename)

        if target.exists():
            logger.warning("Target file already exists: %s", target.name)
            return Result.ok(
                msg=f"Target file already exists: {target.name}")

        res = await upload_files(target, request, content_length=content_length)
        logger.info(f"File uploaded successfully: {res[0]}")
        return Result.ok(msg="File uploaded successfully", data={"filename": res[0], "size": res[1]})
    except ClientDisconnect:
        logger.warning("Client disconnected during upload")
        return JSONResponse(status_code=499, content={"detail": "Client Closed Request"})
    except Exception as e:
        logger.warning(str(e))
        return Result.fail(msg=str(e))


# 如果某些文件上传后没有通过校验，用户需要重新上传这些文件
# 是否将没有通过校验的文件直接删除？方便用户再次上传对的文件？
# 这里返回没有通过md5校验的文件列表，前端可以提示用户重新上传

class FilesList(BaseModel):
    files: list[str]


@file_router.post("/pipeline/rawdata_md5_check/")
async def rawdata_md5_check(request: Request,
                            current_user: Annotated[User, Depends(get_current_active_user)],
                            files: FilesList = Body(..., description="List of filenames to check MD5")):
    user = current_user.username
    rawdata_path = Path(UPLOAD_RAWDATA_PATH, user, "rawdata").resolve()

    # 去重保持顺序
    files_to_check = files.files
    seen = set()
    files_to_check = [f for f in files_to_check if not (
        f in seen or seen.add(f))]

    redis = request.app.state.redis

    # 从 Redis 读取“文件名->MD5”映射，若无则从样本表重建并缓存
    md5_blob = await redis.get(f"{user}_files_md5")
    logger.info(f"files_md5 for user {user} recovered from redis.")
    if isinstance(md5_blob, (bytes, bytearray)):
        md5_blob = md5_blob.decode()

    files_md5: dict[str, str] = json.loads(md5_blob)
    logger.info(f"files_md5 for user {user} loaded successfully.")

    expected_files = set(files_md5.keys())

    # 分类本次请求文件
    unknown = [f for f in files_to_check if f not in expected_files]
    missing_on_disk = [f for f in files_to_check
                       if f in expected_files and not (rawdata_path / f).exists()]
    checkable = [f for f in files_to_check
                 if f in expected_files and (rawdata_path / f).exists()]

    # 对可校验文件执行 MD5 校验
    ok, invalid_md5 = UploadFileProcessor.rawdata_validation(
        files_md5, rawdata_path, checkable
    )

    # 删除 MD5 不匹配的已上传文件，提示重新上传
    deleted = []
    for f in invalid_md5:
        p = rawdata_path / f
        with contextlib.suppress(Exception):
            if p.exists():
                p.unlink()
                deleted.append(f)
                logger.warning(f"MD5 mismatch: deleted file {p}")

    # 本次通过校验的文件
    passed = [f for f in checkable if f not in set(invalid_md5)]
    if passed:
        await redis.sadd(f"{user}_md5_verified", *passed)
        # 刷新过期时间
        await redis.expire(f"{user}_md5_verified", Redis_expires)

    # 已通过集合与剩余待通过文件
    verified_raw = await redis.smembers(f"{user}_md5_verified")
    verified = {v.decode() if isinstance(v, (bytes, bytearray)) else str(v)
                for v in (verified_raw or set())}
    remaining_files = sorted(list(expected_files - verified))

    # 失败详情（含三类原因）
    invalid_detail = (
        [{"file": f, "reason": "not_expected"} for f in unknown] +
        [{"file": f, "reason": "missing_on_disk"} for f in missing_on_disk] +
        [{"file": f, "reason": "md5_mismatch"} for f in invalid_md5]
    )

    progress = {"verified": len(verified), "total": len(expected_files)}
    data = {
        "invalid_files": invalid_detail,
        "remaining_files": remaining_files,
        "deleted_files": deleted,  # 这些文件已被服务器删除，需要重新上传
        "progress": progress,
    }

    if invalid_detail:
        return Result.fail(msg="Some files failed MD5 check. Mismatched files were deleted, please re-upload.",
                           data=data)
    else:
        return Result.ok(msg="MD5 check passed for given files.", data=data)


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
