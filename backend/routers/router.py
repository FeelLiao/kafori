from fastapi import APIRouter

from backend.routers.file_routers import file_router
from backend.routers.analysis_routers import analysis_router
from backend.routers.validation import validation_router

router = APIRouter()
router.include_router(file_router)
router.include_router(analysis_router)
router.include_router(validation_router)
