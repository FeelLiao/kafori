from fastapi import APIRouter
from backend.api.api_routers import file_router
from backend.db.db_routers import db_router

router = APIRouter()
router.include_router(file_router)
router.include_router(db_router)
