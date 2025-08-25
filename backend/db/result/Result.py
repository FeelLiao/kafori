from typing import Any, Generic, TypeVar
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """
    统一返回结果
    code   : 0 – 成功, 1 – 失败
    message: 提示信息
    data   : 业务数据
    """
    code: int = Field(..., description="0 成功 1 失败")
    message: str = Field(..., description="提示信息")
    data: T | None = Field(None, description="业务数据")

    # ---------- 静态工厂方法 ----------
    @staticmethod
    def success(data: T | None = None) -> "Result[T]":
        return Result(code=0, message="操作成功", data=data)

    @staticmethod
    def error(message: str = "操作失败") -> "Result[Any]":
        return Result(code=1, message=message, data=None)

    # 带自定义提示信息的重载
    @staticmethod
    def ok(msg: str, data: T | None = None) -> "Result[T]":
        return Result(code=0, message=msg, data=data)

    @staticmethod
    def fail(msg: str) -> "Result[Any]":
        return Result(code=1, message=msg, data=None)


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
