from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON, TEXT
from sqlmodel import Field, SQLModel


class BaseDownloadContent(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None


class BaseTgContent(BaseDownloadContent):
    id: UUID = Field(default_factory=uuid4, nullable=False, primary_key=True)
    name: str
    language: Optional[str]
    category: Optional[str]
    timeStampLoad: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    timeStampUpdated: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    url: str = Field(default=None, nullable=False, sa_column_kwargs={"unique": True})


class Channel(BaseTgContent, table=True):
    countSubscribers: int


class Bot(BaseTgContent, table=True):
    pass


class Sticker(BaseTgContent, table=True):
    files: List[str] = Field(sa_column=Column(JSON))


class MediaOut(BaseTgContent):
    countSubscribers: Optional[int] = None
    files: Optional[List[str]] = None
