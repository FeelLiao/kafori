from fastapi import APIRouter
from backend.routers.file_routers import file_router
from backend.routers.db_routers import db_router

router = APIRouter()
router.include_router(file_router)
router.include_router(db_router)
