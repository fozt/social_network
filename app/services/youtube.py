import cachetools.func
import youtube_dl
from loguru import logger
from pydantic import HttpUrl

from app.schemas.youtube import YoutubeInfo


@cachetools.func.ttl_cache(maxsize=None, ttl=60 * 60 * 2)
def get_info_by_url(webpage_url: HttpUrl) -> YoutubeInfo:
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            data = ydl.extract_info(webpage_url, download=False)
        except youtube_dl.DownloadError as exc:
            raise ValueError(exc)
        try:
            video_url = next(
                filter(lambda x: x["ext"] in ("mp4", "m4a"), data["requested_formats"])
            )["url"]
            return YoutubeInfo(
                id=data["id"],
                title=data["title"],
                video_url=video_url,
                image_url=data["thumbnail"],
                like_count=data.get("like_count"),
                view_count=data["view_count"],
                channel=data["channel"],
                webpage_url=data["webpage_url"],
                description=data["description"],
                tags=data["tags"],
            )
        except:
            msg = "Invalid parsing Youtube data"
            logger.exception(msg)
            raise ValueError(msg)
