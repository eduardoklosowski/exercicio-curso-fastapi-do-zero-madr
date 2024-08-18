from datetime import datetime, timedelta
from random import randint
from zoneinfo import ZoneInfo

import jwt
from freezegun import freeze_time

from madr.security import create_access_token, get_password_hash, verify_password
from madr.settings import Settings
from tests.utils import randstr


class TestPasswordHash:
    def test_password(self) -> None:
        password = randstr()

        hash_ = get_password_hash(password)

        assert verify_password(password, hash_)

    def test_invalid_password(self) -> None:
        password = randstr()

        hash_ = get_password_hash(password)

        assert not verify_password(password + '0', hash_)


class TestAccessToken:
    settings = Settings()

    def test_token(self) -> None:
        timenow = int(datetime.now(ZoneInfo('UTC')).timestamp())
        timenow = randint(timenow, timenow + int(timedelta(days=365).total_seconds()))
        email = f'{randstr()}@test.com'

        with freeze_time(datetime.fromtimestamp(timenow, ZoneInfo('UTC'))):
            returned = create_access_token(email=email)
        token_decoded = jwt.decode(
            returned, algorithms=[self.settings.ACCESS_TOKEN_ALGORITHM], key=self.settings.SECRET_KEY
        )

        assert token_decoded == {
            'sub': email,
            'exp': timenow + self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
