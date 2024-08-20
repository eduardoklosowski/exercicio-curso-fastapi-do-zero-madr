from http import HTTPStatus
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from madr.database import T_DbSession
from madr.errors import InvalidLoginError
from madr.models import User
from madr.schemas import Token
from madr.security import create_access_token, verify_password

router = APIRouter(tags=['Auth'])

T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post(
    '/token',
    summary='Entra no sistema e gera token de acesso',
    status_code=HTTPStatus.OK,
)
def login_for_access_token(dbsession: T_DbSession, form_data: T_OAuth2Form) -> Token:
    user = dbsession.scalar(
        sa.select(User).where(sa.or_(User.email == form_data.username, User.username == form_data.username))
    )
    if not user or not verify_password(form_data.password, user.password):
        raise InvalidLoginError

    return Token(access_token=create_access_token(email=user.email))
