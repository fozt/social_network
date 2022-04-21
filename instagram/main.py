from fastapi import FastAPI, APIRouter

from .logic import InstagramMediaDownloader
from .scheme import Media, MediaResponse, User, Settings, MediaType

settings = Settings()
app = FastAPI()
instagram_router = APIRouter()


@instagram_router.get("/get-media-info", response_model=MediaResponse)
async def info(media_type: MediaType, media_id: str) -> MediaResponse:
    media = Media.from_orm(HANDLER_MEDIA[media_type](media_id.strip('/')))
    user = User.from_orm(media_downloader.get_user(media.owner_username))
    return MediaResponse(user=user, media=media, media_type=media_type)


media_downloader = InstagramMediaDownloader(settings.instagram_login, settings.instagram_password)
HANDLER_MEDIA = {
    MediaType.POST: media_downloader.get_post,
    MediaType.REELS: media_downloader.get_reels,
    MediaType.STORIES: lambda media_id: media_downloader.get_stories(int(media_id)),
}

app.include_router(router=instagram_router, prefix='/instagram')
