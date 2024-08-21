from http import HTTPStatus
from random import randint

from faker import Faker
from fastapi.testclient import TestClient

from madr.models import Livro, Romancista
from madr.utils import sanitize


class TestCreateLivro:
    url = '/livro'

    def test_create_livro(self, client: TestClient, romancista: Romancista, token: str, faker: Faker) -> None:
        title = faker.text(40)
        year = randint(1990, 2100)

        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': title,
                'year': year,
                'romancista_id': romancista.id,
            },
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {
            'id': 1,
            'title': sanitize(title),
            'year': year,
            'romancista_id': romancista.id,
        }

    def test_without_token(self, client: TestClient, romancista: Romancista, faker: Faker) -> None:
        response = client.post(
            self.url,
            json={
                'title': faker.text(40),
                'year': randint(1900, 2100),
                'romancista_id': romancista.id,
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}

    def test_empty_title(self, client: TestClient, romancista: Romancista, token: str) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': '',
                'year': randint(1900, 2100),
                'romancista_id': romancista.id,
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'title']

    def test_empty_title_after_sanitize(self, client: TestClient, romancista: Romancista, token: str) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': '?',
                'year': randint(1900, 2100),
                'romancista_id': romancista.id,
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'title']

    def test_title_already_exists(self, client: TestClient, romancista: Romancista, token: str, livro: Livro) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': livro.title,
                'year': randint(1900, 2100),
                'romancista_id': romancista.id,
            },
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {'message': 'Livro já consta no MADR'}

    def test_invalid_year(self, client: TestClient, romancista: Romancista, token: str, faker: Faker) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': faker.text(40),
                'year': -1,
                'romancista_id': romancista.id,
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'year']

    def test_romancista_not_found(self, client: TestClient, token: str, faker: Faker) -> None:
        response = client.post(
            self.url,
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': faker.text(40),
                'year': randint(1900, 2100),
                'romancista_id': 1,
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Romancista não consta no MADR'}
