from fastapi import APIRouter, UploadFile, File
from typing import Tuple
import logging
from io import BytesIO

from backend.api.files import UploadFileProcessor


file_router = APIRouter()
logger = logging.getLogger(__name__)


# def sample_sheet_validation(file: BytesIO) -> Tuple[bool, str]:
#     """
#     Process the uploaded file.
#     Args:
#         file (BytesIO): The uploaded file in memory.
#     Returns:
#         Tuple[bool, str]: A tuple containing a success flag and a message.
#     """
#     try:
#         processor = UploadFileProcessor(file)
#         processor.valid_dataframe
#         return True, "Sample sheet uploaded successfully."
#     except FileNotFoundError as e:
#         logger.error(f"File not found: {e}")
#         return False, str(e)
#     except ValueError as e:
#         logger.error(f"Invalid file format: {e}")
#         return False, str(e)
#     except RuntimeError as e:
#         logger.error(f"Error processing file: {e}")
#         return False, str(e)
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         return False, "An unexpected error occurred."


@file_router.post("/pipeline/sample_sheet_upload/")
async def upload_xlsx(file: UploadFile = File(...)):
    sample_sheet = BytesIO(await file.read())
    # rel = sample_sheet_validation(sample_sheet)
    rel = (True, "Sample sheet uploaded successfully.")  # Placeholder for actual processing logic
    return {"success": rel[0], "msg": rel[1]}


# @file_router.post("/pipeline/gene_expression_upload/")
# async def upload_xlsx_stream(file: UploadFile = File(...), user_id: str = ""):
#     gene_expression = BytesIO(await file.read())

#     rel = process_gene_expression(gene_expression)
#     return {"success": rel[0], "msg": rel[1]}


# @file_router.post("/pipeline/rawdata_upload/")
# async def upload_metadata(file: UploadFile = File(...), user_id: str = ""):
#     metadata = BytesIO(await file.read())

#     rel = process_rawdata(metadata)
#     return {"success": rel[0], "msg": rel[1]}
