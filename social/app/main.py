import time

from fastapi import FastAPI, Request

from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(openapi_url="/openapi.json")
app.include_router(router=api_router)


@app.middleware("http")
async def save_base_absolute_url(request: Request, call_next):
    settings.BASE_URL = str(request.base_url)
    response = await call_next(request)
    return response
