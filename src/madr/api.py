from http import HTTPStatus
from importlib.metadata import version

import sqlalchemy as sa
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import SQLAlchemyError

from .database import T_DbSession
from .errors import HttpError
from .schemas import ApiInfo, Message

app = FastAPI(
    title='MADR API',
    description='Meu Acervo Digital de Romances',
    version=version('madr'),
)


@app.exception_handler(HttpError)
async def http_error_handler(_request: Request, exc: HttpError) -> Response:
    return JSONResponse(
        status_code=exc.http_status_code,
        content=Message(message=exc.message).model_dump(),
    )


@app.get(
    '/',
    summary='Informações da API',
    tags=['API'],
    status_code=HTTPStatus.OK,
)
def index() -> ApiInfo:
    return ApiInfo(
        name=app.title,
        description=app.description,
        version=app.version,
    )


@app.get(
    '/health',
    summary='Health check da API',
    tags=['API'],
    status_code=HTTPStatus.OK,
)
def health(dbsession: T_DbSession) -> Message:
    try:
        dbsession.execute(sa.select(sa.text('1'))).one()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='Error on database connection') from e

    return Message(message='OK')
