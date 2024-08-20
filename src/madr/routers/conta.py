from http import HTTPStatus

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from madr.database import T_DbSession
from madr.errors import ConflictError, UnauthorizedError
from madr.models import User
from madr.schemas import Message, UserPublic, UserSchema
from madr.security import T_CurrentUser

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


@router.put(
    '/{user_id}',
    summary='Atualiza conta no MADR',
    status_code=HTTPStatus.OK,
)
def update_user(dbsession: T_DbSession, current_user: T_CurrentUser, user: UserSchema, user_id: int) -> UserPublic:
    if current_user.id != user_id:
        raise UnauthorizedError

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = user.password
    try:
        dbsession.commit()
    except IntegrityError as e:
        if e.orig.__class__.__name__ == 'UniqueViolation':
            raise ConflictError(resource='Conta') from None
        raise  # pragma: no cover
    dbsession.refresh(current_user)

    return UserPublic.model_validate(current_user)


@router.delete(
    '/{user_id}',
    summary='Remove conta no MADR',
    status_code=HTTPStatus.OK,
)
def delete_user(dbsession: T_DbSession, current_user: T_CurrentUser, user_id: int) -> Message:
    if current_user.id != user_id:
        raise UnauthorizedError

    dbsession.delete(current_user)
    dbsession.commit()

    return Message(message='Conta deletada com sucesso')
