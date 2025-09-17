from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
import warnings
from tortoise.contrib.fastapi import register_tortoise
import os
from backend.db.decorator.Redis import register_redis

from backend.db.config.redis_conf import build_redis_pool
from backend.db.config.tortoise_conf import TORTOISE_ORM
from backend.db.exceptions.handlers import ExceptionHandler
from backend.routers.router import router
from backend.logger import init_global_logger
from backend.api.config import config
from backend.analysis.analysis_base import RProcessorPoolMP


logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize the global logger
init_global_logger(config.log_dir)

# Determine the number of R cores to start
R_CORE = os.cpu_count() if int(config.start_r_core) == 0 else int(config.start_r_core)


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.r_processor = RProcessorPoolMP(pool_maxsize=R_CORE)
    logger.info("RProcessor initialized")
    app.state.redis = build_redis_pool()
    logger.info("Redis connection pool initialized")

    yield
    app.state.r_processor.close()
    logger.info("RProcessor shut down")
    await app.state.redis.close()
    logger.info("Redis connection pool closed")


app = FastAPI(lifespan=lifespan,
              title="Kafori API",
              description="API for Kafori project",
              version="1.0.0",
              license_info={
                  "name": "MIT",
                  "url": "https://opensource.org/licenses/MIT"
              }
              )
app.include_router(router)

# 1) Mysql “一键注册”
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # 生产环境用迁移
    add_exception_handlers=False,
)

# 2) Redis “一键注册”
register_redis(
    app,
    generate_schemas=False,        # 占位，与 Tortoise 对齐
    add_exception_handlers=False,
)

# 注册异常处理器（一行即可）
ExceptionHandler.register(app)




# 配置CORS中间件
origins = [
    "*"  # 允许的前端域名
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的来源
    allow_credentials=True,  # 允许发送Cookie
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的头
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
