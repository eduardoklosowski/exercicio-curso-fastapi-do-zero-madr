from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt
from pwdlib import PasswordHash

from madr.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()


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
