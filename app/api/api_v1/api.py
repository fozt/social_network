from fastapi import APIRouter

from app.api.api_v1.endpoints import instagram, telegram, youtube

api_router = APIRouter()
api_router.include_router(instagram.router, prefix="/instagram", tags=["instagram"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
