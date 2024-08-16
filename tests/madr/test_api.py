from contextlib import suppress
from http import HTTPStatus
from importlib.metadata import version

import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestIndex:
    url = '/'

    def test_get_api_info(self, client: TestClient) -> None:
        response = client.get(self.url)

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            'name': 'MADR API',
            'description': 'Meu Acervo Digital de Romances',
            'version': version('madr'),
        }


class TestHealth:
    url = '/health'

    def test_health_on_ok(self, client: TestClient) -> None:
        response = client.get(self.url)

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'message': 'OK'}

    def test_health_on_database_connection_error(self, client: TestClient, dbsession: Session) -> None:
        with suppress(Exception):
            dbsession.execute(sa.text('SELECT * FROM table_not_exists'))

        response = client.get(self.url)

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json() == {'detail': 'Error on database connection'}
