from fastapi import APIRouter, UploadFile, File, Depends, Request
from typing import Tuple
import logging
from io import BytesIO
from typing import Annotated

from backend.api.files import UploadFileProcessor
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
        sample_sheet = UploadFileProcessor(file, name)
        sample_sheet_data = sample_sheet.read_xlsx()
        valid = sample_sheet.data_validation(sample_sheet_data)
        if valid:
            sample_save = sample_sheet_data.to_parquet()
            await redis.set(f"{user}", sample_save, ex=600)
            logger.info(
                f"Sample sheet for user {user} saved to redis successfully.")
        return valid, "Sample sheet uploaded successfully."
    except Exception as e:
        return False, str(e)


@file_router.post("/pipeline/sample_sheet/")
async def upload_xlsx(request: Request,
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
async def upload_xlsx_stream(request: Request,
                             current_user: Annotated[User, Depends(get_current_active_user)],
                             file: UploadFile = File(...,
                                                     description="Upload gene expression file standard by tpm method")):
    user = current_user.username
    gene_tpm_name = file.filename
    gene_tpm = BytesIO(await file.read())

    rel = process_gene_tpm(
        gene_tpm, user=user, name=gene_tpm_name, request=request)
    return {"success": rel[0], "msg": rel[1]}


# @file_router.post("/pipeline/rawdata_upload/")
# async def upload_metadata(file: UploadFile = File(...), user_id: str = ""):
#     metadata = BytesIO(await file.read())

#     rel = process_rawdata(metadata)
#     return {"success": rel[0], "msg": rel[1]}
