from http import HTTPStatus

import jwt
from fastapi.testclient import TestClient
from freezegun import freeze_time

from madr.security import create_access_token
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


class TestRefreshAccessToken:
    url = '/refresh-token'
    settings = Settings()

    def test_refresh_token(self, client: TestClient, user: UserWithAttrs, token: str) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
        )
        new_token = response.json()
        decoded = jwt.decode(
            new_token['access_token'], algorithms=[self.settings.ACCESS_TOKEN_ALGORITHM], key=self.settings.SECRET_KEY
        )

        assert response.status_code == HTTPStatus.OK
        assert new_token['token_type'] == 'bearer'
        assert decoded['sub'] == user.model.email

    def test_invalid_token(self, client: TestClient) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': 'Bearer invalid'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'message': 'Não autorizado'}

    def test_expired_token(self, client: TestClient, user: UserWithAttrs) -> None:
        with freeze_time('2000-01-01 00:00:00'):
            token = create_access_token(email=user.model.email)

        with freeze_time('2020-01-01 00:00:00'):
            response = client.post(
                self.url,
                headers={'Authorization': f'Bearer {token}'},
            )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'message': 'Não autorizado'}

    def test_token_without_email(self, client: TestClient) -> None:
        token = jwt.encode({}, algorithm=self.settings.ACCESS_TOKEN_ALGORITHM, key=self.settings.SECRET_KEY)

        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'message': 'Não autorizado'}

    def test_token_with_user_not_in_database(self, client: TestClient) -> None:
        token = create_access_token(email='invalid')

        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'message': 'Não autorizado'}
