from http import HTTPStatus

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from madr.database import T_DbSession
from madr.errors import ConflictError
from madr.models import Romancista
from madr.schemas import RomancistaPublic, RomancistaSchema
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
