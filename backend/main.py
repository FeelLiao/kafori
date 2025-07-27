from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
import warnings

from backend.routers import router
from backend.logger import init_global_logger
from backend.settings import LOG_FILE
from backend.analysis.analysis_base import RProcessor


logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize the global logger
init_global_logger(LOG_FILE)


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.r_processor = RProcessor(pool_size=8)
    logger.info("RProcessor initialized")
    yield
    app.state.r_processor.close()
    logger.info("RProcessor shut down")

app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
