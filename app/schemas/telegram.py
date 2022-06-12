from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, validator

from app.models.telegram import BaseDownloadContent


class Types(str, Enum):
    CHANNEL = "channel"
    BOT = "bot"
    STICKER = "sticker"


class Sorting(str, Enum):
    ASC_TIME = "asc_time"
    DESC_TIME = "desc_time"
    ASC_SUBSCRIPTIONS = "asc_subscriptions"
    DESC_SUBSCRIPTIONS = "desc_subscriptions"


class TgQueryInput(BaseModel):
    url: HttpUrl
    category: Optional[str]
    language: Optional[str]


class TgQuery(TgQueryInput):
    id: Optional[UUID] = Field(default_factory=uuid4)
    name: Optional[str]
    type: Optional[Types]

    @validator("name", always=True)
    def get_name(cls, v, values, **kwargs):
        return values["url"].rstrip("/").split("/")[-1]

    @validator("type", always=True)
    def get_type(cls, v, values, **kwargs):
        url = values["url"].rstrip("/")
        if url.lower().endswith("bot"):
            return Types.BOT
        elif "t.me/addstickers" in url:
            return Types.STICKER
        elif "t.me" in url:
            return Types.CHANNEL
        else:
            raise ValueError("Invalid telegram content URL.")


class ChannelDownload(BaseDownloadContent):
    countSubscribers: int


class BotDownload(BaseDownloadContent):
    pass


class StickerDownload(BaseDownloadContent):
    files: List[str]
