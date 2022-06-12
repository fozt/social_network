import logging

from fastapi import APIRouter, HTTPException
from instaloader import BadResponseException, InvalidArgumentException

from app.core.config import settings
from app.schemas.instagram import Media, MediaResponse, MediaType, User
from app.services.instagram import InstagramMediaDownloader

router = APIRouter()


@router.get("/get-media-info", response_model=MediaResponse)
def info(mediaType: MediaType, mediaId: str) -> MediaResponse:
    try:
        media = Media.from_orm(HANDLER_MEDIA[mediaType](mediaId.strip("/")))
        user = User.from_orm(media_downloader.get_user(media.owner_username))
    except (BadResponseException, InvalidArgumentException, AttributeError, ValueError):
        logging.error(f"Failed download {mediaId=}. Maybe profile is private")
        logging.exception("get-media-info Error")
        raise HTTPException(status_code=404, detail="Media not found")
    return MediaResponse(user=user, media=media, media_type=mediaType)


media_downloader = InstagramMediaDownloader(
    settings.INSTAGRAM_LOGIN, settings.INSTAGRAM_PASSWORD
)
HANDLER_MEDIA = {
    MediaType.POST: media_downloader.get_post,
    MediaType.REELS: media_downloader.get_reels,
    MediaType.STORIES: lambda media_id: media_downloader.get_stories(int(media_id)),
}
