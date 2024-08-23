from http import HTTPStatus

import sqlalchemy as sa
from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from madr.database import T_DbSession
from madr.errors import ConflictError, NotFoundError
from madr.models import Livro, Romancista
from madr.schemas import NO_ARG, LivroPatch, LivroPublic, LivroSchema, Message
from madr.security import T_CurrentUser

router = APIRouter(prefix='/livro', tags=['Livro'])


@router.post(
    '/',
    summary='Cria livro no MADR',
    status_code=HTTPStatus.CREATED,
)
def create_livro(dbsession: T_DbSession, _user: T_CurrentUser, livro: LivroSchema) -> LivroPublic:
    db_romancista = dbsession.scalar(sa.select(Romancista).where(Romancista.id == livro.romancista_id))
    if not db_romancista:
        raise NotFoundError(resource='Romancista')

    db_livro = Livro(title=livro.title, year=livro.year, romancista=db_romancista)
    dbsession.add(db_livro)
    try:
        dbsession.commit()
    except IntegrityError as e:
        if e.orig.__class__.__name__ == 'UniqueViolation':
            raise ConflictError(resource='Livro') from None
        raise  # pragma: no cover
    dbsession.refresh(db_livro)

    return LivroPublic.model_validate(db_livro)


@router.get(
    '/{livro_id}',
    summary='Recupera livro pelo id no MADR',
    status_code=HTTPStatus.OK,
)
def get_livro(dbsession: T_DbSession, livro_id: int) -> LivroPublic:
    db_livro = dbsession.scalar(sa.select(Livro).where(Livro.id == livro_id))
    if not db_livro:
        raise NotFoundError(resource='Livro')

    return LivroPublic.model_validate(db_livro)


@router.patch(
    '/{livro_id}',
    summary='Atualiza livro no MADR',
    status_code=HTTPStatus.OK,
)
def patch_livro(dbsession: T_DbSession, _user: T_CurrentUser, livro: LivroPatch, livro_id: int) -> LivroPublic:
    db_livro = dbsession.scalar(sa.select(Livro).where(Livro.id == livro_id))
    if not db_livro:
        raise NotFoundError(resource='Livro')

    for field in livro.model_fields:
        value = getattr(livro, field)
        if value == NO_ARG:
            continue
        setattr(db_livro, field, value)
    try:
        dbsession.commit()
    except IntegrityError as e:
        if e.orig.__class__.__name__ == 'UniqueViolation':
            raise ConflictError(resource='Livro') from None
        if e.orig.__class__.__name__ == 'ForeignKeyViolation':
            raise NotFoundError(resource='Romancista') from None
        raise  # pragma: no cover
    dbsession.refresh(db_livro)

    return LivroPublic.model_validate(db_livro)


@router.delete(
    '/{livro_id}',
    summary='Romove livro no MADR',
    status_code=HTTPStatus.OK,
)
def delete_romancista(dbsession: T_DbSession, _user: T_CurrentUser, livro_id: int) -> Message:
    deleted_id = dbsession.scalar(sa.delete(Livro).where(Livro.id == livro_id).returning(Livro.id))
    if not deleted_id:
        raise NotFoundError(resource='Livro')

    dbsession.commit()

    return Message(message='Livro deletado com sucesso')
