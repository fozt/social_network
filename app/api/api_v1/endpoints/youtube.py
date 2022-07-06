from fastapi import APIRouter, HTTPException, status
from pydantic import HttpUrl

from app.schemas.youtube import YoutubeInfo
from app.services.youtube import get_info_by_url

router = APIRouter()


@router.get("/", response_model=YoutubeInfo)
async def get_video_info(url: HttpUrl):
    try:
        result = get_info_by_url(url)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
