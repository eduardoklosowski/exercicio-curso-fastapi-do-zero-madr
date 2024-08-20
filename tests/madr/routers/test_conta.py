from http import HTTPStatus

import sqlalchemy as sa
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from madr.models import User
from madr.security import verify_password
from madr.utils import sanitize
from tests.utils import UserWithAttrs


class TestCreateUser:
    url = '/conta'

    def test_create_user(self, client: TestClient, dbsession: Session, faker: Faker) -> None:
        email = faker.email()
        username = faker.user_name()
        password = faker.password()

        response = client.post(
            self.url,
            json={
                'email': email,
                'username': username,
                'password': password,
            },
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {
            'id': 1,
            'email': email,
            'username': sanitize(username),
        }
        assert verify_password(password, dbsession.scalars(sa.select(User).where(User.id == 1)).one().password)

    def test_empty_email(self, client: TestClient, faker: Faker) -> None:
        response = client.post(
            self.url,
            json={
                'email': '',
                'username': faker.user_name(),
                'password': faker.password(),
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'email']

    def test_invalid_email(self, client: TestClient, faker: Faker) -> None:
        response = client.post(
            self.url,
            json={
                'email': 'invalid',
                'username': faker.user_name(),
                'password': faker.password(),
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'email']

    def test_email_already_exists(self, client: TestClient, faker: Faker, other_user: UserWithAttrs) -> None:
        response = client.post(
            self.url,
            json={
                'email': other_user.model.email,
                'username': faker.user_name(),
                'password': faker.password(),
            },
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {'message': 'Conta já consta no MADR'}

    def test_empty_username(self, client: TestClient, faker: Faker) -> None:
        response = client.post(
            self.url,
            json={
                'email': faker.email(),
                'username': '',
                'password': faker.password(),
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'username']

    def test_empty_username_after_sanitize(self, client: TestClient, faker: Faker) -> None:
        response = client.post(
            self.url,
            json={
                'email': faker.email(),
                'username': '?',
                'password': faker.password(),
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'username']

    def test_username_already_exists(self, client: TestClient, faker: Faker, other_user: UserWithAttrs) -> None:
        response = client.post(
            self.url,
            json={
                'email': faker.email(),
                'username': other_user.model.username,
                'password': faker.password(),
            },
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {'message': 'Conta já consta no MADR'}

    def test_empty_password(self, client: TestClient, faker: Faker) -> None:
        response = client.post(
            self.url,
            json={
                'email': faker.email(),
                'username': faker.user_name(),
                'password': '',
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'password']
