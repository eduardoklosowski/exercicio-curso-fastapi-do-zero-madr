from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

import jwt
import sqlalchemy as sa
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from madr.database import T_DbSession
from madr.errors import UnauthorizedError
from madr.models import User
from madr.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_password_hash(password: str, /) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str, /) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(*, email: str) -> str:
    return jwt.encode(
        {
            'sub': email,
            'exp': datetime.now(ZoneInfo('UTC')) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        algorithm=settings.ACCESS_TOKEN_ALGORITHM,
        key=settings.SECRET_KEY,
    )


T_Token = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(dbsession: T_DbSession, token: T_Token) -> User:
    try:
        payload = jwt.decode(token, algorithms=[settings.ACCESS_TOKEN_ALGORITHM], key=settings.SECRET_KEY)
    except jwt.PyJWTError:
        raise UnauthorizedError from None

    email: str = payload.get('sub', '')
    if not email:
        raise UnauthorizedError

    user = dbsession.scalar(sa.select(User).where(User.email == email))
    if not user:
        raise UnauthorizedError

    return user


T_CurrentUser = Annotated[User, Depends(get_current_user)]
