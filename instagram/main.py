import logging

from fastapi import FastAPI, APIRouter, HTTPException
from instaloader import BadResponseException, InvalidArgumentException

from .logic import InstagramMediaDownloader
from .scheme import Media, MediaResponse, User, Settings, MediaType

settings = Settings()
app = FastAPI()
instagram_router = APIRouter()


@instagram_router.get("/get-media-info", response_model=MediaResponse)
async def info(mediaType: MediaType, mediaId: str) -> MediaResponse:
    try:
        media = Media.from_orm(HANDLER_MEDIA[mediaType](mediaId.strip('/')))
        user = User.from_orm(media_downloader.get_user(media.owner_username))
    except (BadResponseException, InvalidArgumentException, AttributeError, ValueError):
        logging.error(f'Failed download {mediaId=}. Maybe profile is private')
        logging.exception('get-media-info Error')
        raise HTTPException(status_code=404, detail="Media not found")
    return MediaResponse(user=user, media=media, media_type=mediaType)


media_downloader = InstagramMediaDownloader(settings.instagram_login, settings.instagram_password)
HANDLER_MEDIA = {
    MediaType.POST: media_downloader.get_post,
    MediaType.REELS: media_downloader.get_reels,
    MediaType.STORIES: lambda media_id: media_downloader.get_stories(int(media_id)),
}

app.include_router(router=instagram_router, prefix='/instagram')
