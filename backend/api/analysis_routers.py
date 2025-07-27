from fastapi import APIRouter, Request
from typing import Tuple
import logging
from io import BytesIO

analysis_router = APIRouter()
logger = logging.getLogger(__name__)


async def run_r_analysis(request: Request, r_code: str, **kwargs):
    r_processor = request.app.state.r_processor
    result = await r_processor.async_run_analysis(r_code, **kwargs)
    return result

@analysis_router.get("/transcripts/ex_class")
async def ex_class():
    pass

@analysis_router.get("/transcripts/tpm_viz")
async def tpm_viz(request: Request):
    result = await tpm(request)
    return {"result": str(result)}
    