from http import HTTPStatus
from random import randint

import sqlalchemy as sa
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from madr.models import Livro, Romancista
from madr.utils import sanitize
from tests.factories import LivroFactory, RomancistaFactory


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


class TesteGetLivro:
    url = '/livro/{livro_id}'

    def test_get_livro(self, client: TestClient, livro: Livro) -> None:
        response = client.get(
            self.url.format(livro_id=livro.id),
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': livro.id,
            'title': livro.title,
            'year': livro.year,
            'romancista_id': livro.romancista_id,
        }

    def test_not_found(self, client: TestClient) -> None:
        response = client.get(
            self.url.format(livro_id=1),
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Livro não consta no MADR'}


class TestListLivro:
    url = '/livro'

    def test_list_livro(self, client: TestClient, dbsession: Session) -> None:
        livros = LivroFactory.build_batch(randint(3, 10))
        dbsession.add_all(livros)
        dbsession.commit()

        response = client.get(
            self.url,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'livros': [
                {'id': livro.id, 'title': livro.title, 'year': livro.year, 'romancista_id': livro.romancista_id}
                for livro in livros
            ]
        }

    def test_empty_list(self, client: TestClient) -> None:
        response = client.get(
            self.url,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'livros': []}

    def test_partial_title(self, client: TestClient, dbsession: Session) -> None:
        livros = [LivroFactory.build(title=f'{'a' if i % 2 else 'b'}{i}') for i in range(randint(3, 10))]
        dbsession.add_all(livros)
        dbsession.commit()

        response = client.get(
            self.url,
            params={'title': 'a'},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'livros': [
                {'id': livro.id, 'title': livro.title, 'year': livro.year, 'romancista_id': livro.romancista_id}
                for livro in livros
                if 'a' in livro.title
            ]
        }

    def test_year_title(self, client: TestClient, dbsession: Session) -> None:
        year = randint(1900, 2100)

        livros = [LivroFactory.build(year=year if i % 2 else year + 10) for i in range(randint(3, 10))]
        dbsession.add_all(livros)
        dbsession.commit()

        response = client.get(
            self.url,
            params={'year': year},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'livros': [
                {'id': livro.id, 'title': livro.title, 'year': livro.year, 'romancista_id': livro.romancista_id}
                for livro in livros
                if livro.year == year
            ]
        }

    def test_offset(self, client: TestClient, dbsession: Session) -> None:
        livros = LivroFactory.build_batch(randint(30, 40))
        dbsession.add_all(livros)
        dbsession.commit()

        response = client.get(
            self.url,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'livros': [
                {'id': livro.id, 'title': livro.title, 'year': livro.year, 'romancista_id': livro.romancista_id}
                for livro in livros[:20]
            ]
        }

        for i in range(20, len(livros)):
            response = client.get(
                self.url,
                params={'offset': i},
            )

            assert response.status_code == HTTPStatus.OK
            assert response.json() == {
                'livros': [
                    {'id': livro.id, 'title': livro.title, 'year': livro.year, 'romancista_id': livro.romancista_id}
                    for livro in livros[i : i + 20]
                ]
            }

    def test_limit(self, client: TestClient, dbsession: Session) -> None:
        livros = LivroFactory.build_batch(21)
        dbsession.add_all(livros)
        dbsession.commit()

        for i in range(20):
            response = client.get(
                self.url,
                params={'limit': i},
            )

            assert response.status_code == HTTPStatus.OK
            assert response.json() == {
                'livros': [
                    {'id': livro.id, 'title': livro.title, 'year': livro.year, 'romancista_id': livro.romancista_id}
                    for livro in livros[:i]
                ]
            }

    def test_all_params(self, client: TestClient, dbsession: Session) -> None:
        year = randint(1900, 2100)

        livros = [
            LivroFactory.build(title=f'{'b' if i % 2 else 'a'}{i}', year=year if i % 4 else year + 10)
            for i in range(randint(30, 40))
        ]
        dbsession.add_all(livros)
        dbsession.commit()
        livros_filtered = [livro for livro in livros if 'b' in livro.title and livro.year == year]

        for i in range(len(livros_filtered)):
            response = client.get(
                self.url,
                params={'title': 'b', 'year': year, 'offset': i, 'limit': 5},
            )

            assert response.status_code == HTTPStatus.OK
            assert response.json() == {
                'livros': [
                    {'id': livro.id, 'title': livro.title, 'year': livro.year, 'romancista_id': livro.romancista_id}
                    for livro in livros_filtered[i : i + 5]
                ]
            }


class TestPatchLivro:
    url = '/livro/{livro_id}'

    def test_patch_all_fields(
        self, client: TestClient, dbsession: Session, livro: Livro, token: str, faker: Faker
    ) -> None:
        new_romancista = RomancistaFactory.build()
        dbsession.add(new_romancista)
        dbsession.commit()

        title = faker.text(40)
        year = randint(1900, 2100)

        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': title,
                'year': year,
                'romancista_id': new_romancista.id,
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': livro.id,
            'title': sanitize(title),
            'year': year,
            'romancista_id': new_romancista.id,
        }

    def test_patch_title_field(self, client: TestClient, livro: Livro, token: str, faker: Faker) -> None:
        title = faker.text(40)

        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'title': title},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': livro.id,
            'title': sanitize(title),
            'year': livro.year,
            'romancista_id': livro.romancista_id,
        }

    def test_patch_year_field(self, client: TestClient, livro: Livro, token: str) -> None:
        year = randint(1900, 2100)

        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'year': year},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': livro.id,
            'title': livro.title,
            'year': year,
            'romancista_id': livro.romancista_id,
        }

    def test_patch_romancista_id_field(self, client: TestClient, dbsession: Session, livro: Livro, token: str) -> None:
        new_romancista = RomancistaFactory.build()
        dbsession.add(new_romancista)
        dbsession.commit()

        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'romancista_id': new_romancista.id},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': livro.id,
            'title': livro.title,
            'year': livro.year,
            'romancista_id': new_romancista.id,
        }

    def test_patch_with_no_fields(self, client: TestClient, livro: Livro, token: str) -> None:
        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'id': livro.id,
            'title': livro.title,
            'year': livro.year,
            'romancista_id': livro.romancista_id,
        }

    def test_without_token(self, client: TestClient, livro: Livro) -> None:
        response = client.patch(
            self.url.format(livro_id=livro.id),
            json={},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}

    def test_not_found(self, client: TestClient, token: str) -> None:
        response = client.patch(
            self.url.format(livro_id=1),
            headers={'Authorization': f'Bearer {token}'},
            json={},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Livro não consta no MADR'}

    def test_empty_title(self, client: TestClient, livro: Livro, token: str) -> None:
        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'title': ''},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'title']

    def test_empty_title_after_sanitize(self, client: TestClient, livro: Livro, token: str) -> None:
        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'title': '?'},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'] == ['body', 'title']

    def test_title_already_exists(self, client: TestClient, dbsession: Session, livro: Livro, token: str) -> None:
        other_livro = LivroFactory.build()
        dbsession.add(other_livro)
        dbsession.commit()

        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'title': other_livro.title},
        )

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {'message': 'Livro já consta no MADR'}

    def test_invalid_year(self, client: TestClient, livro: Livro, token: str) -> None:
        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'year': -1},
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json()['detail'][0]['loc'][:2] == ['body', 'year']

    def test_romancista_not_found(self, client: TestClient, livro: Livro, token: str) -> None:
        response = client.patch(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
            json={'romancista_id': livro.romancista_id + 1},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Romancista não consta no MADR'}


class TestDeleteLivro:
    url = '/livro/{livro_id}'

    def test_delete_livro(self, client: TestClient, dbsession: Session, livro: Livro, token: str) -> None:
        response = client.delete(
            self.url.format(livro_id=livro.id),
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'message': 'Livro deletado com sucesso'}
        assert dbsession.scalar(sa.select(Livro).where(Livro.id == livro.id)) is None

    def test_without_token(self, client: TestClient, livro: Livro) -> None:
        response = client.delete(
            self.url.format(livro_id=livro.id),
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}

    def test_not_found(self, client: TestClient, token: str) -> None:
        response = client.delete(
            self.url.format(livro_id=1),
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {'message': 'Livro não consta no MADR'}
