from fastapi import FastAPI

from app.api.api_v1.api import api_router

app = FastAPI(openapi_url="/openapi.json")
app.include_router(router=api_router)