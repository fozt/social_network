from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class YoutubeInfo(BaseModel):
    id: str
    title: str
    description: str
    video_url: HttpUrl
    image_url: HttpUrl
    tags: List[str]
    webpage_url: HttpUrl
    view_count: int
    like_count: Optional[int]
    channel: str
