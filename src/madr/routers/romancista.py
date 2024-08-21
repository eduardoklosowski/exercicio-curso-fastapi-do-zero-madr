from http import HTTPStatus

import sqlalchemy as sa
from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from madr.database import T_DbSession
from madr.errors import ConflictError, NotFoundError
from madr.models import Romancista
from madr.schemas import Message, RomancistaPublic, RomancistaSchema
from madr.security import T_CurrentUser

router = APIRouter(prefix='/romancista', tags=['Romancista'])


@router.post(
    '/',
    summary='Cria romancista no MADR',
    status_code=HTTPStatus.CREATED,
)
def create_romancista(dbsession: T_DbSession, _user: T_CurrentUser, romancista: RomancistaSchema) -> RomancistaPublic:
    db_romancista = Romancista(name=romancista.name)
    dbsession.add(db_romancista)
    try:
        dbsession.commit()
    except IntegrityError as e:
        if e.orig.__class__.__name__ == 'UniqueViolation':
            raise ConflictError(resource='Romancista') from None
        raise  # pragma: no cover
    dbsession.refresh(db_romancista)

    return RomancistaPublic.model_validate(db_romancista)


@router.get(
    '/{romancista_id}',
    summary='Recupera romancista pelo id no MADR',
    status_code=HTTPStatus.OK,
)
def get_romancista(dbsession: T_DbSession, romancista_id: int) -> RomancistaPublic:
    db_romancista = dbsession.scalar(sa.select(Romancista).where(Romancista.id == romancista_id))
    if not db_romancista:
        raise NotFoundError(resource='Romancista')

    return RomancistaPublic.model_validate(db_romancista)


@router.put(
    '/{romancista_id}',
    summary='Atualiza romancista no MADR',
    status_code=HTTPStatus.OK,
)
def update_romancista(
    dbsession: T_DbSession, _user: T_CurrentUser, romancista: RomancistaSchema, romancista_id: int
) -> RomancistaPublic:
    db_romancista = dbsession.scalar(sa.select(Romancista).where(Romancista.id == romancista_id))
    if not db_romancista:
        raise NotFoundError(resource='Romancista')

    db_romancista.name = romancista.name
    try:
        dbsession.commit()
    except IntegrityError as e:
        if e.orig.__class__.__name__ == 'UniqueViolation':
            raise ConflictError(resource='Romancista') from None
        raise  # pragma: no cover
    dbsession.refresh(db_romancista)

    return RomancistaPublic.model_validate(db_romancista)


@router.delete(
    '/{romancista_id}',
    summary='Remove romancista no MADR',
    status_code=HTTPStatus.OK,
)
def delete_romancista(dbsession: T_DbSession, _user: T_CurrentUser, romancista_id: int) -> Message:
    deleted_id = dbsession.scalar(sa.delete(Romancista).where(Romancista.id == romancista_id).returning(Romancista.id))
    if not deleted_id:
        raise NotFoundError(resource='Romancista')

    dbsession.commit()

    return Message(message='Romancista deletado com sucesso')
