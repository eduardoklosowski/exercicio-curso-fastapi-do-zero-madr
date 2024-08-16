from http import HTTPStatus
from importlib.metadata import version

import sqlalchemy as sa
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .database import T_DbSession
from .schemas import ApiInfo, Message

app = FastAPI(
    title='MADR API',
    description='Meu Acervo Digital de Romances',
    version=version('madr'),
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
