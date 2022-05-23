from datetime import datetime
from enum import Enum
from typing import Optional

from humps import camelize
from pydantic import BaseModel, Field


class Media(BaseModel):
    owner_username: str
    url: str
    date_utc: datetime
    likes: Optional[int] = Field(alias="countLikes")
    comments: Optional[int] = Field(alias="countComments")
    caption: str = Field(default=None, alias="description")

    class Config:
        orm_mode = True
        alias_generator = camelize
        allow_population_by_field_name = True


class MediaType(str, Enum):
    STORIES = "stories"
    POST = "post"
    REELS = "reels"


class User(BaseModel):
    followees: int
    followers: int
    full_name: str
    external_url: Optional[str]
    profile_pic_url: str
    username: str
    userid: int
    mediacount: int
    igtvcount: int
    is_verified: bool
    is_private: bool

    class Config:
        orm_mode = True
        alias_generator = camelize
        allow_population_by_field_name = True


class MediaResponse(BaseModel):
    media: Media
    user: User
    media_type: MediaType

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
