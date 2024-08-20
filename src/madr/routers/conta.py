from http import HTTPStatus

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from madr.database import T_DbSession
from madr.errors import ConflictError
from madr.models import User
from madr.schemas import UserPublic, UserSchema

router = APIRouter(prefix='/conta', tags=['Conta'])


@router.post(
    '/',
    summary='Cria conta no MADR',
    status_code=HTTPStatus.CREATED,
)
def create_user(dbsession: T_DbSession, user: UserSchema) -> UserPublic:
    db_user = User(email=user.email, username=user.username, password=user.password)
    dbsession.add(db_user)
    try:
        dbsession.commit()
    except IntegrityError as e:
        if e.orig.__class__.__name__ == 'UniqueViolation':
            raise ConflictError(resource='Conta') from None
        raise  # pragma: no cover
    dbsession.refresh(db_user)

    return UserPublic.model_validate(db_user)
