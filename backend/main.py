from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
import warnings
from tortoise.contrib.fastapi import register_tortoise

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


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.r_processor = RProcessorPoolMP(pool_maxsize=8)
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

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # 生产环境用迁移
    add_exception_handlers=True,
)

# 注册异常处理器（一行即可）
ExceptionHandler.register(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}
