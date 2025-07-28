from fastapi import APIRouter, UploadFile, File
from typing import Tuple
import logging
from io import BytesIO


file_router = APIRouter()
logger = logging.getLogger(__name__)


def process_sample_sheet(file: BytesIO) -> Tuple[bool, str]:
    """
    Process the uploaded file.
    Args:
        file (BytesIO): The uploaded file in memory.
    Returns:
        Tuple[bool, str]: A tuple containing a success flag and a message.
    """
    pass


@file_router.post("/pipeline/sample_sheet_upload/")
async def upload_xlsx(file: UploadFile = File(...)):
    sample_sheet = BytesIO(await file.read())
    rel = process_sample_sheet(sample_sheet)
    return {"success": rel[0], "msg": rel[1]}
