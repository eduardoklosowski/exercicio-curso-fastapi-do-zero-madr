from http import HTTPStatus

from faker import Faker
from fastapi.testclient import TestClient

from madr.models import Romancista
from madr.utils import sanitize


class TestCreateRomancista:
    url = '/romancista'

    def test_create_romancista(self, client: TestClient, token: str, faker: Faker) -> None:
        name = faker.name()

        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={'name': name},
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {
            'id': 1,
            'name': sanitize(name),
        }

    def test_without_token(self, client: TestClient, faker: Faker) -> None:
        response = client.post(
            self.url,
            json={'name': faker.name()},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}

    def test_empty_name(self, client: TestClient, token: str) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={'name': ''},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'name']

    def test_empty_name_after_sanitize(self, client: TestClient, token: str) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={'name': '?'},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'name']

    def test_name_already_exists(self, client: TestClient, token: str, romancista: Romancista) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={'name': romancista.name},
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {'message': 'Romancista já consta no MADR'}
