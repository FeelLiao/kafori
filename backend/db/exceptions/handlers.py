from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from tortoise.exceptions import IntegrityError
from backend.db.result.JsonResult import JSONResult

import logging
logger = logging.getLogger(__name__)

class ExceptionHandler:
    """
    统一异常处理器
    1. ValidationError    -> 422
    2. IntegrityError     -> 400
    3. 其他 Exception     -> 500
    """

    @staticmethod
    def register(app):
        """一次性注册到 FastAPI"""
        app.add_exception_handler(
            RequestValidationError, ExceptionHandler.request_validation_error)
        app.add_exception_handler(
            ValidationError,  ExceptionHandler.validation_error)
        app.add_exception_handler(
            IntegrityError,   ExceptionHandler.integrity_error)
        app.add_exception_handler(
            Exception,        ExceptionHandler.generic_error)

    # ---------- 具体处理函数 ----------
    @staticmethod
    async def request_validation_error(request: Request, exc: Exception) -> JSONResult:
        logger.error(exc)
        return JSONResult.error(message=str(exc))

    @staticmethod
    async def validation_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(exc)
        return JSONResult.error(message=str(exc), status_code=422)

    @staticmethod
    async def integrity_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(exc)
        return JSONResult.error(message=str(exc), status_code=400)

    @staticmethod
    async def generic_error(request: Request, exc: Exception) -> JSONResponse:
        # 可在此处记录日志
        logger.error(exc)
        return JSONResult.error(message=str(exc), status_code=500)
