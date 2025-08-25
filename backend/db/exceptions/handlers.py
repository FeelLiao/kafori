from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from tortoise.exceptions import IntegrityError
from backend.db.result.JsonResult import JSONResult


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
            ValidationError,  ExceptionHandler.validation_error)
        app.add_exception_handler(
            IntegrityError,   ExceptionHandler.integrity_error)
        app.add_exception_handler(
            Exception,        ExceptionHandler.generic_error)

    # ---------- 具体处理函数 ----------
    @staticmethod
    async def validation_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResult.error("参数校验失败", status_code=422)

    @staticmethod
    async def integrity_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResult.error("数据已存在或约束冲突", status_code=400)

    @staticmethod
    async def generic_error(request: Request, exc: Exception) -> JSONResponse:
        # 可在此处记录日志
        return JSONResult.error("服务器内部错误", status_code=500)
