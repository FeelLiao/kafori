from fastapi import APIRouter, UploadFile, File, Depends, Request
from typing import Tuple
import logging
from io import BytesIO
from typing import Annotated

from backend.api.files import UploadFileProcessor, FileType, GeneDataType, PutDataBaseWrapper
from backend.routers.validation import get_current_active_user, User
from backend.db.result.Result import Result
from backend.db.interface import PutDataBaseInterface


file_router = APIRouter()
logger = logging.getLogger(__name__)


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
            await redis.set(f"{user}_sample_sheet", sample_save, ex=600)
            logger.info(
                f"Sample sheet for user {user} saved to redis successfully.")
            return valid, "Sample sheet uploaded successfully."
        else:
            return False, "Sample sheet uploaded failed."
    except Exception as e:
        return False, str(e)


async def process_gene_ex(file: BytesIO, user: str, name: str,
                          request: Request, type: GeneDataType) -> Tuple[bool, str]:
    """
    Process the uploaded gene expression file.
    Args:
        file (BytesIO): The uploaded file in memory.
    Returns:
        Tuple[bool, str]: A tuple containing a success flag and a message.
    """
    try:
        redis = request.app.state.redis
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
            await redis.set(f"{user}_gene_{type}", gene_save, ex=600)
            logger.info(
                f"Gene expression data {type} for user {user} saved to redis successfully.")
        return valid, f"Gene expression data {type} uploaded successfully."
    except Exception as e:
        return False, str(e)


async def process_db_upload(user: str, request: Request) -> Tuple[bool, str]:
    try:
        redis = request.app.state.redis
        sample_sheet = BytesIO(await redis.get(f"{user}_sample_sheet"))
        sample_sheet_data = UploadFileProcessor.read_file(sample_sheet, file_type=FileType.parquet)
        logger.info(f"sample sheet file extracted successfully for user {user}.")
        gene_tpm = BytesIO(await redis.get(f"{user}_gene_{GeneDataType.tpm}"))
        gene_tpm_data = UploadFileProcessor.read_file(gene_tpm, file_type=FileType.parquet)
        logger.info(f"gene tpm file extracted successfully for user {user}.")
        gene_counts = BytesIO(await redis.get(f"{user}_gene_{GeneDataType.counts}"))
        gene_counts_data = UploadFileProcessor.read_file(gene_counts, file_type=FileType.parquet)
        logger.info(f"gene counts file extracted successfully for user {user}.")

        data_base_wrapper = PutDataBaseWrapper(sample_sheet_data, gene_tpm_data, gene_counts_data)
        exp_class_communication = data_base_wrapper.communicate_id_in_db()
        exp_class_communication_r = await PutDataBaseInterface.exclass_processing(exp_class_communication)
        logger.info(f"Experiment class has put into database successfully for user {user}.")

        exp_sheet, sample_sheet = data_base_wrapper.db_insert(exp_class_communication_r)
        tpm, counts = data_base_wrapper.expression_wrapper(sample_sheet)

        exp_valid = await PutDataBaseInterface.put_experiment(exp_sheet)
        logger.info(f"Experiment data has been put into database successfully for user {user}.")
        sample_valid = await PutDataBaseInterface.put_sample(sample_sheet)
        logger.info(f"Sample data has been put into database successfully for user {user}.")
        tpm_valid = await PutDataBaseInterface.put_gene_tpm(tpm)
        logger.info(f"Gene TPM data has been put into database successfully for user {user}.")
        counts_valid = await PutDataBaseInterface.put_gene_counts(counts)
        logger.info(f"Gene Counts data has been put into database successfully for user {user}.")

        valid = [exp_valid, sample_valid, tpm_valid, counts_valid]
        if all(valid):
            return True, "Database data uploaded successfully."
        else:
            return False, "Database data upload failed."
    except Exception as e:
        logger.error(f"Error in putting data into database for user {user}: {e}", exc_info=True)
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


# @file_router.post("/pipeline/rawdata/")
# async def upload_metadata(file: UploadFile = File(...), user_id: str = ""):
#     metadata = BytesIO(await file.read())

#     rel = process_rawdata(metadata)
#     return {"success": rel[0], "msg": rel[1]}

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
