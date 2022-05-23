from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, validator

from app.models.telegram import BaseDownloadContent, BaseTgContent


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
    url: str
    category: Optional[str]
    language: Optional[str]


class TgQuery(TgQueryInput):
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
        else:
            return Types.CHANNEL

    # @property
    # def name(self):
    #     return self._name
    #
    # @property
    # def type(self):
    #     return self._type


class ChannelDownload(BaseDownloadContent):
    countSubscribers: int


class BotDownload(BaseDownloadContent):
    pass


class StickerDownload(BaseDownloadContent):
    files: List[str]


# class StickerOut(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     imageUrl: Optional[str] = None

#
# class StickerOut(BaseModel):
#     name: str
#     language: Optional[str]
#     category: Optional[str]
#     timeStampLoad: datetime
#     timeStampUpdated: datetime
#     url: str
#     files: List[str]
#     title: str
#     description: Optional[str]
#     imageUrl: Optional[str]
#
#     class Config:
#         orm_mode = True
#
#
# class ChannelOut(BaseTgContent):
#     countSubscribers: int
#
#
# class BotOut(BaseTgContent):
#     pass
