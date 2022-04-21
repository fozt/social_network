from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, BaseSettings


class Media(BaseModel):
    owner_username: str
    url: str
    date_utc: datetime

    class Config:
        orm_mode = True


class MediaType(str, Enum):
    STORIES = 'stories'
    POST = 'post'
    REELS = 'reels'


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


class MediaResponse(BaseModel):
    media: Media
    user: User
    media_type: MediaType


class Settings(BaseSettings):
    instagram_login: str
    instagram_password: str

    class Config:
        env_file = ".env"
