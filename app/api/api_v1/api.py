from fastapi import APIRouter

from app.api.api_v1.endpoints import instagram, telegram

api_router = APIRouter()
api_router.include_router(instagram.router, prefix="/instagram")
api_router.include_router(telegram.router, prefix="/telegram")
