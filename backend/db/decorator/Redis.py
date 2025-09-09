# redis_register.py
from functools import wraps
from fastapi import FastAPI
from backend.db.config.redis_conf import build_redis_pool   # 你的 yaml/pydantic 配置

Redis: FastAPI = None   # 占位，启动时注入

def register_redis(
        app: FastAPI,
        *,
        generate_schemas: bool = False,   # 占位，保持与 Tortoise 同名
        add_exception_handlers: bool = False
):
    """
    等价于 register_tortoise，但针对 Redis
    """
    global Redis
    Redis = app

    @app.on_event("startup")
    async def _startup():
        app.state.redis = build_redis_pool()  # 复用之前的 build_redis_pool
        # await get_conn().set("val","432")
        await app.state.redis.flushall()
        print("✅ Redis pool created")

    @app.on_event("shutdown")
    async def _shutdown():
        await app.state.redis.close()
        print("❌ Redis pool closed")

    # 可选：统一异常处理
    if add_exception_handlers:
        pass

def get_conn():
    return Redis.state.redis


