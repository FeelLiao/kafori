from fastapi import APIRouter, UploadFile, File
from fastapi import BackgroundTasks
from pathlib import Path

from .utils import UploadFileProcessor

file_router = APIRouter()

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)
UPLOAD_DATA_DIR = UPLOAD_DIR / "data"
UPLOAD_DATA_DIR.mkdir(exist_ok=True)

FILE_PROCESS_STATUS = {}


def process_file(file_path: Path):
    """
    Background task to process the uploaded file.
    Args:
        file_path (Path): The path to the uploaded file.
    """
    filename = file_path.name
    FILE_PROCESS_STATUS[filename] = {"status": "processing", "detail": None}
    try:
        FILE_PROCESS_STATUS[filename] = {
            "status": "processing", "detail": "file format validating"}
        processor = UploadFileProcessor(file_path)
        processor.valid_dataframe
        FILE_PROCESS_STATUS[filename] = {
            "status": "processing", "detail": "file format validated"}
    except Exception as e:
        FILE_PROCESS_STATUS[filename] = {"status": "error", "detail": str(e)}
        print(f"Error processing file {file_path.name}: {e}")

    FILE_PROCESS_STATUS[filename] = {
        "status": "processing", "detail": "Raw date md5 sum checking"}
    md5_results = processor.rawdata_validation(UPLOAD_DATA_DIR)
    if md5_results[0]:
        FILE_PROCESS_STATUS[filename] = {
            "status": "completed", "detail": "Raw data md5 sum check passed."}
    else:
        FILE_PROCESS_STATUS[filename] = {
            "status": "error", "detail": "Raw data md5 sum check failed. "
            "The following files are not passed: " + ", ".join(md5_results[1])}


@file_router.post("/pipeline/sample_sheet_upload/")
async def upload_xlsx(background_tasks: BackgroundTasks,
                      file: UploadFile = File(...)):

    global LAST_FILENAME
    LAST_FILENAME = None

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    FILE_PROCESS_STATUS[file.filename] = {"status": "pending", "detail": None}
    LAST_FILENAME = file.filename
    background_tasks.add_task(process_file, file_path)
    return {"success": True, "msg": f"File {file.filename} uploaded successfully."}


@file_router.get("/pipeline/sample_sheet_status/")
async def filestatus():
    if LAST_FILENAME is None:
        return {"success": False, "msg": "No file uploaded yet."}
    status = FILE_PROCESS_STATUS.get(LAST_FILENAME)
    if status is None:
        return {"success": False, "msg": "No status found."}
    return {"success": True, "status": status["status"], "detail": status["detail"]}
