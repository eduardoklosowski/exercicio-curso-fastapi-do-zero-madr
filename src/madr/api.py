from http import HTTPStatus
from importlib.metadata import version

from fastapi import FastAPI

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
def health() -> Message:
    return Message(message='OK')
