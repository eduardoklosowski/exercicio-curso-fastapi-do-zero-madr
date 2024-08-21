from http import HTTPStatus
from random import randint

import sqlalchemy as sa
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from madr.models import Romancista
from madr.utils import sanitize
from tests.factories import RomancistaFactory


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


class TesteGetRomancista:
    url = '/romancista/{romancista_id}'

    def test_get_romancista(self, client: TestClient, romancista: Romancista) -> None:
        response = client.get(
            self.url.format(romancista_id=romancista.id),
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': romancista.id,
            'name': romancista.name,
        }

    def test_not_found(self, client: TestClient) -> None:
        response = client.get(
            self.url.format(romancista_id=1),
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Romancista não consta no MADR'}


class TestListRomancista:
    url = '/romancista'

    def test_list_romancista(self, client: TestClient, dbsession: Session) -> None:
        romancistas = RomancistaFactory.build_batch(randint(3, 10))
        dbsession.add_all(romancistas)
        dbsession.commit()

        response = client.get(
            self.url,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'romancistas': [{'id': romancista.id, 'name': romancista.name} for romancista in romancistas]
        }

    def test_empty_list(self, client: TestClient) -> None:
        response = client.get(
            self.url,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'romancistas': []}

    def test_partial_name(self, client: TestClient, dbsession: Session) -> None:
        romancistas = [RomancistaFactory.build(name=f'{'a' if i % 2 else 'b'}{i}') for i in range(randint(3, 10))]
        dbsession.add_all(romancistas)
        dbsession.commit()

        response = client.get(
            self.url,
            params={'name': 'a'},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'romancistas': [
                {'id': romancista.id, 'name': romancista.name} for romancista in romancistas if 'a' in romancista.name
            ]
        }

    def test_offset(self, client: TestClient, dbsession: Session) -> None:
        romancistas = RomancistaFactory.build_batch(randint(30, 40))
        dbsession.add_all(romancistas)
        dbsession.commit()

        response = client.get(
            self.url,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'romancistas': [{'id': romancista.id, 'name': romancista.name} for romancista in romancistas[:20]]
        }

        for i in range(20, len(romancistas)):
            response = client.get(
                self.url,
                params={'offset': i},
            )

            assert response.status_code == HTTPStatus.OK
            assert response.json() == {
                'romancistas': [
                    {'id': romancista.id, 'name': romancista.name} for romancista in romancistas[i : i + 20]
                ]
            }

    def test_limit(self, client: TestClient, dbsession: Session) -> None:
        romancistas = RomancistaFactory.build_batch(21)
        dbsession.add_all(romancistas)
        dbsession.commit()

        for i in range(20):
            response = client.get(
                self.url,
                params={'limit': i},
            )

            assert response.status_code == HTTPStatus.OK
            assert response.json() == {
                'romancistas': [{'id': romancista.id, 'name': romancista.name} for romancista in romancistas[:i]]
            }

    def test_all_params(self, client: TestClient, dbsession: Session) -> None:
        romancistas = [RomancistaFactory.build(name=f'{'a' if i % 2 else 'b'}{i}') for i in range(randint(30, 40))]
        dbsession.add_all(romancistas)
        dbsession.commit()
        romancistas_filtrados = [romancista for romancista in romancistas if 'b' in romancista.name]

        for i in range(len(romancistas_filtrados)):
            response = client.get(
                self.url,
                params={'name': 'b', 'offset': i, 'limit': 5},
            )

            assert response.status_code == HTTPStatus.OK
            assert response.json() == {
                'romancistas': [
                    {'id': romancista.id, 'name': romancista.name} for romancista in romancistas_filtrados[i : i + 5]
                ]
            }


class TestUpdateRomancista:
    url = '/romancista/{romancista_id}'

    def test_update_romancista(self, client: TestClient, romancista: Romancista, token: str, faker: Faker) -> None:
        name = faker.name()

        response = client.put(
            self.url.format(romancista_id=romancista.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'name': name},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': romancista.id,
            'name': sanitize(name),
        }

    def test_without_token(self, client: TestClient, romancista: Romancista, faker: Faker) -> None:
        response = client.put(
            self.url.format(romancista_id=romancista.id),
            json={'name': faker.name()},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}

    def test_not_found(self, client: TestClient, token: str, faker: Faker) -> None:
        response = client.put(
            self.url.format(romancista_id=1),
            headers={'Authorization': f'Bearer {token}'},
            json={'name': faker.name()},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Romancista não consta no MADR'}

    def test_empty_name(self, client: TestClient, romancista: Romancista, token: str) -> None:
        response = client.put(
            self.url.format(romancista_id=romancista.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'name': ''},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'name']

    def test_empty_name_after_sanitize(self, client: TestClient, romancista: Romancista, token: str) -> None:
        response = client.put(
            self.url.format(romancista_id=romancista.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'name': '?'},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'name']

    def test_name_already_exists(
        self, client: TestClient, dbsession: Session, romancista: Romancista, token: str, faker: Faker
    ) -> None:
        other_romancista = RomancistaFactory.build(name=sanitize(faker.name()))
        dbsession.add(other_romancista)
        dbsession.commit()

        response = client.put(
            self.url.format(romancista_id=romancista.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'name': other_romancista.name},
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {'message': 'Romancista já consta no MADR'}


class TestDeleteRomancista:
    url = '/romancista/{romancista_id}'

    def test_delete_romancista(
        self, client: TestClient, dbsession: Session, romancista: Romancista, token: str
    ) -> None:
        response = client.delete(
            self.url.format(romancista_id=romancista.id),
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'message': 'Romancista deletado com sucesso'}
        assert dbsession.scalar(sa.select(Romancista).where(Romancista.id == romancista.id)) is None

    def test_without_token(self, client: TestClient, romancista: Romancista) -> None:
        response = client.delete(
            self.url.format(romancista_id=romancista.id),
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}

    def test_not_found(self, client: TestClient, token: str) -> None:
        response = client.delete(
            self.url.format(romancista_id=1),
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Romancista não consta no MADR'}
