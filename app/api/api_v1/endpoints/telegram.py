import os
from typing import List, Optional, Union

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.crud.telegram import crud_tg
from app.db.session import create_db_and_tables
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
    obj.files = obj.files
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


# @router.get("/", response_model=Union[Channel, Bot, Sticker])
# def add_object(query: TgQueryInput):
#     try:
#         return crud_tg.create(TgQuery.parse_obj(query.dict()))
#     except IntegrityError:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Resource already exists')


# @app.route('/telegram/getObject', methods=['GET'])
# def get_object():
#     args = request.args
#     try:
#         url = args['url']
#     except KeyError:
#         error_text = (
#             f'/telegram/getObject with data = {json} (not found required field `url`)'
#         )
#         logger.error(error_text)
#         send_tg_message(f'{error_text} error')
#         return error_text, 400
#     try:
#         name = channel_data.get_name(url)
#         type_obj = channel_data.get_type(url)
#
#         obj = channel_data.get_object_info(name, type_obj)
#         return jsonify(obj)
#     except Exception as e:
#         error_text = f'/telegram/getObject with {args=}'
#         logger.error(error_text)
#         send_tg_message(f'{error_text} error {traceback.format_exc()}')
#         logger.exception(e)
#         return error_text, 400
#
#
# @app.route('/telegram/getObjectsList', methods=['GET'])
# def get_channels():
#     args = request.args
#     try:
#         type_obj = args['type']
#         category = args.get('category')
#         language = args.get('language')
#         sort_mode = args.get('sort')
#         offset = int(args.get('offset', 0))
#         size = int(args.get('size', 20))
#     except KeyError:
#         error_text = (
#             f'/telegram/getObjectsList with {args=} (not found required field `type`)'
#         )
#         logger.error(error_text)
#         send_tg_message(f'{error_text} error')
#         return error_text, 400
#     try:
#         return jsonify(
#             channel_data.sort(
#                 channel_data.get_items(
#                     channel_data.sort(
#                         channel_data.filter(type_obj, category, language), sort_mode
#                     ),
#                     offset,
#                     size,
#                 ),
#                 sort_mode,
#             )
#         )
#     except Exception as e:
#         error_text = f'/telegram/getObjectsList with {json=}'
#         logger.error(error_text)
#         send_tg_message(f'{error_text} error {traceback.format_exc()}')
#         logger.exception(e)
#         return error_text, 400
