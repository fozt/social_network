import base64
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode, urljoin

import cachetools.func
import requests
from fastapi import HTTPException
from sqlmodel import Session, select
from starlette import status

from app.core.config import settings
from app.db.session import engine
from app.models.telegram import Bot, Channel, MediaPhoto, Sticker
from app.schemas.telegram import Sorting, TgQuery, Types
from app.services.telegram import tg_downloader


def generate_url(url_endpoint: str, params: Dict):
    query_string = urlencode(params)
    url = f"{url_endpoint}?{query_string}"
    return url


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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Resource already exists"
            )
        content = self.download_content(tg_query.json())
        content.imageUrl = generate_url(
            urljoin(settings.BASE_URL, "/telegram/image"), {"url": tg_query.url}
        )
        print(f"{content=}")
        with Session(engine) as session:
            session.add(content)
            session.commit()
            session.refresh(content)
            # session.delete(content)
            # session.commit()
        return content

    # @cachetools.func.ttl_cache(maxsize=None, ttl=60 * 60 * 24)
    def download_content(self, tg_query_json: str):
        tg_query = TgQuery.parse_raw(tg_query_json)
        try:
            data = self.content_mapping_download[tg_query.type](tg_query)
            print(f"{data.imageUrl=}")
            with Session(engine) as session:
                if session.get(MediaPhoto, data.url) is None:
                    content = MediaPhoto(
                        url=data.url,
                        media=base64.b64encode(
                            requests.get(data.imageUrl).content
                        ).decode(),
                    )
                    session.add(content)
                    session.commit()
            data.imageUrl = generate_url(
                urljoin(settings.BASE_URL, "/telegram/image"), {"url": data.url}
            )
            return data

        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

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
            data = session.get(self.table_mapping[tg_query.type], tg_query.url)
            return data

    def get_media(self, url) -> bytes:
        with Session(engine) as session:
            media_b64 = session.get(MediaPhoto, url)
        if media_b64 is None:
            raise HTTPException(status_code=404)
        return base64.b64decode(media_b64.media.encode())

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
