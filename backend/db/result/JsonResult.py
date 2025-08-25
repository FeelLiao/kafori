from typing import Any
from fastapi.responses import JSONResponse


class JSONResult:
    """统一 JSON 响应封装"""
    @staticmethod
    def success(data: Any = None) -> JSONResponse:
        return JSONResponse(
            status_code=200,
            content={"code": 0, "message": "操作成功", "data": data}
        )

    @staticmethod
    def error(message: str = "操作失败", status_code: int = 400) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"code": 1, "message": message, "data": None}
        )

    @staticmethod
    def ok(message: str = "OK", data: Any = None, status_code: int = 200) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"code": 0, "message": message, "data": data}
        )

    @staticmethod
    def fail(message: str, status_code: int = 400) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"code": 1, "message": message, "data": None}
        )
