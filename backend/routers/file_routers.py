from fastapi import APIRouter, UploadFile, File, Depends, Request
from typing import Tuple
import logging
from io import BytesIO
from typing import Annotated

from backend.api.files import UploadFileProcessor, FileType, GeneDataType
from backend.routers.validation import get_current_active_user, User


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
    return {"success": rel[0], "msg": rel[1]}


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
    return {"success": rel[0], "msg": rel[1]}


@file_router.post("/pipeline/gene_ex_counts/")
async def upload_gene_ex_counts(request: Request,
                                current_user: Annotated[User, Depends(get_current_active_user)],
                                file: UploadFile = File(...,
                                                        description="Upload gene expression file standard by counts method")):
    user = current_user.username
    gene_counts_name = file.filename
    gene_counts = BytesIO(await file.read())
    rel = await process_gene_ex(
        gene_counts, user=user, name=gene_counts_name,
        request=request, type=GeneDataType.counts)
    return {"success": rel[0], "msg": rel[1]}


# @file_router.post("/pipeline/rawdata/")
# async def upload_metadata(file: UploadFile = File(...), user_id: str = ""):
#     metadata = BytesIO(await file.read())

#     rel = process_rawdata(metadata)
#     return {"success": rel[0], "msg": rel[1]}
