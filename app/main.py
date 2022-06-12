import os.path
import sys

from fastapi import FastAPI
from loguru import logger

from app.api.api_v1.api import api_router

logger.remove()
logger.add(sys.stderr, backtrace=False, diagnose=False)
logger.add("out.log", backtrace=False, diagnose=False)

app = FastAPI(openapi_url="/openapi.json")
app.include_router(router=api_router)

if not os.path.exists("./data"):
    os.mkdir("./data")
