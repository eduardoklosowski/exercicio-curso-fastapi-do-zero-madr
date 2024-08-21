from http import HTTPStatus

import sqlalchemy as sa
from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from madr.database import T_DbSession
from madr.errors import ConflictError, NotFoundError
from madr.models import Livro, Romancista
from madr.schemas import LivroPublic, LivroSchema
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
