from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.crud.telegram import crud_tg
from app.models.telegram import MediaOut
from app.schemas.telegram import Sorting, TgQuery, TgQueryInput, Types

router = APIRouter()


@router.post("/", response_model=MediaOut)
def add_object(query: TgQueryInput):
    try:
        query = TgQuery.parse_obj(query.dict())
        obj = crud_tg.create(query)
        return MediaOut.from_orm(obj)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Resource already exists"
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/object", response_model=MediaOut)
def get_object(url: str):
    obj = crud_tg.get(TgQuery(url=url))
    if obj is None:
        raise HTTPException(status_code=404)
    return obj


@router.get("/preview", response_model=MediaOut)
def get_object(url: str):
    obj = crud_tg.get(TgQuery(url=url))
    if obj is None:
        obj = crud_tg.download_content(TgQuery(url=url).json())
    if obj is None:
        raise HTTPException(status_code=404)
    return obj


@router.get("/", response_model=List[MediaOut])
def get_objects(
    typeObj: Types,
    language: Optional[str] = None,
    category: Optional[str] = None,
    sortBy: Optional[Sorting] = None,
    size: int = 20,
    offset: int = 0,
):
    obj = crud_tg.get_all(
        type_obj=typeObj,
        category=category,
        language=language,
        sort_by=sortBy,
        size=size,
        offset=offset,
    )
    if obj is None:
        raise HTTPException(status_code=404)
    return obj
