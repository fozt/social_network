import os.path
from typing import List, Optional, Union
from urllib.parse import urljoin

import requests
from loguru import logger
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import engine
from app.models.telegram import Bot, Channel, Sticker
from app.schemas.telegram import Sorting, TgQuery, Types
from app.services.telegram import tg_downloader


class CRUDTg:
    def __init__(self):
        self.content_mapping_download = {
            Types.CHANNEL: self._download_channel,
            Types.BOT: self._download_bot,
            Types.STICKER: self._download_sticker,
        }

        self.table_mapping = {
            Types.CHANNEL: Channel,
            Types.BOT: Bot,
            Types.STICKER: Sticker,
        }

        self.tg_downloader = tg_downloader

    def sort_condition(self, table, condition):
        return {
            Sorting.ASC_TIME: table.timeStampLoad.asc(),
            Sorting.DESC_TIME: table.timeStampLoad.desc(),
            Sorting.ASC_SUBSCRIPTIONS: table.countSubscribers.asc()
            if table == Channel
            else None,
            Sorting.DESC_SUBSCRIPTIONS: table.countSubscribers.desc()
            if table == Channel
            else None,
        }[condition]

    def create(self, tg_query: TgQuery) -> Union[Bot, Channel, Sticker]:
        if self.get(tg_query) is not None:
            raise ValueError
        content = self.download_content(tg_query.json())
        content.imageUrl = content.imageUrl
        with Session(engine) as session:
            session.add(content)
            session.commit()
            session.refresh(content)
        return content

    # @cachetools.func.ttl_cache(maxsize=None, ttl=60 * 60 * 24)
    def download_content(self, tg_query_json: str):
        tg_query = TgQuery.parse_raw(tg_query_json)
        try:
            data = self.content_mapping_download[tg_query.type](tg_query)
        except Exception as exc:
            logger.exception(
                exc,
            )
            raise ValueError("Invalid content")
        if data.imageUrl is not None:
            with open(
                os.path.join(settings.FILES_PATH, f"{tg_query.id.hex}.jpg"), "wb"
            ) as f:
                f.write(requests.get(data.imageUrl).content)
            data.imageUrl = urljoin(settings.FILES_URL, f"{tg_query.id.hex}.jpg")
        return data

    def _download_channel(self, tg_query: TgQuery) -> Channel:
        channel = self.tg_downloader.download_channel_info(tg_query.name)
        return Channel(**channel.dict(), **tg_query.dict())

    def _download_bot(self, tg_query: TgQuery) -> Bot:
        bot = self.tg_downloader.download_bot_info(tg_query.name)
        return Bot(**bot.dict(), **tg_query.dict())

    def _download_sticker(self, tg_query: TgQuery) -> Sticker:
        sticker = self.tg_downloader.download_sticker_info(tg_query.name)

        data = {**sticker.dict(), **tg_query.dict()}
        sticker_res = Sticker.parse_obj(data)
        return sticker_res

    def get(self, tg_query: TgQuery) -> Union[Bot, Channel, Sticker]:
        with Session(engine) as session:
            table = self.table_mapping[tg_query.type]
            query = select(table).where(table.url == tg_query.url)
            data = session.exec(query)
            return data.first()

    def get_categories(self, type_obj: Types):
        table = self.table_mapping[type_obj]
        with Session(engine) as session:
            return session.exec(select(table.category).distinct()).all()

    def get_all(
        self,
        type_obj: Types,
        category: str,
        language: str,
        sort_by: Optional[Sorting],
        size: int = 20,
        offset: int = 0,
    ) -> List[Union[Channel, Bot, Sticker]]:
        with Session(engine) as session:
            table = self.table_mapping[type_obj]
            query = (
                select(table)
                .where(table.language == language if language is not None else True)
                .where(table.category == category if category is not None else True)
                .order_by(
                    self.sort_condition(table, sort_by) if sort_by is not None else True
                )
                .offset(offset)
                .limit(size)
            )
            return session.exec(query).all()


crud_tg = CRUDTg()
