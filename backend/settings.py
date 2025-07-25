from pathlib import Path

# save the uploaded file to a specific directory
UPLOAD_DIR = Path("tests/upstream")
UPLOAD_DIR.mkdir(exist_ok=True)
UPLOAD_DATA_DIR = UPLOAD_DIR / "ngs-test-data"
UPLOAD_DATA_DIR.mkdir(exist_ok=True)

# save the log file to a specific directory
LOG_FILE = Path("tests/logs.log")
