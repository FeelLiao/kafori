from fastapi import APIRouter
from api.api_routers import file_router
from db.db_routers import db_router

router = APIRouter()
router.include_router(file_router)
router.include_router(db_router)
