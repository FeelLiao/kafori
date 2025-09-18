from fastapi import APIRouter
from fastapi.responses import Response
import logging

from backend.api.dl_providers import get_catalog, handle_download
from backend.db.result.Result import Result  # 你的统一返回封装
import backend.api.download.config_download  # noqa: F401

download_router = APIRouter()
logger = logging.getLogger(__name__)


@download_router.get("/download/catalog")
async def download_catalog():
    try:
        res = get_catalog()
        return Result.ok(msg="Success", data=res)
    except Exception as e:
        logger.error("Get download catalog error")
        return Result.error(message=str(e))


@download_router.post("/download/{classes}/{filename}")
async def download_file(classes: str, filename: str) -> Response:
    try:
        cls = handle_download(classes)
        return cls().response(filename)
    except Exception as e:
        logger.error("download error: %s", str(e))
        return Result.error(message=str(e))
