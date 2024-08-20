from http import HTTPStatus

import jwt
from fastapi.testclient import TestClient

from madr.settings import Settings
from tests.utils import UserWithAttrs


class TestLoginForAccessToken:
    url = '/token'
    settings = Settings()

    def test_login_with_email(self, client: TestClient, user: UserWithAttrs) -> None:
        response = client.post(
            self.url,
            data={'username': user.model.email, 'password': user.clean_password},
        )
        token = response.json()
        decoded = jwt.decode(
            token['access_token'], algorithms=[self.settings.ACCESS_TOKEN_ALGORITHM], key=self.settings.SECRET_KEY
        )

        assert response.status_code == HTTPStatus.OK
        assert token['token_type'] == 'bearer'
        assert decoded['sub'] == user.model.email

    def test_login_with_username(self, client: TestClient, user: UserWithAttrs) -> None:
        response = client.post(
            self.url,
            data={'username': user.model.username, 'password': user.clean_password},
        )
        token = response.json()
        decoded = jwt.decode(
            token['access_token'], algorithms=[self.settings.ACCESS_TOKEN_ALGORITHM], key=self.settings.SECRET_KEY
        )

        assert response.status_code == HTTPStatus.OK
        assert token['token_type'] == 'bearer'
        assert decoded['sub'] == user.model.email

    def test_invalid_user(self, client: TestClient) -> None:
        response = client.post(
            self.url,
            data={'username': 'invalid', 'password': 'invalid'},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {'message': 'Email ou senha incorretos'}

    def test_invalid_password(self, client: TestClient, user: UserWithAttrs) -> None:
        response = client.post(
            self.url,
            data={'username': user.model.email, 'password': 'invalid'},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {'message': 'Email ou senha incorretos'}
