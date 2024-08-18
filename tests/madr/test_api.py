from contextlib import suppress
from http import HTTPStatus
from importlib.metadata import version

import pytest
import sqlalchemy as sa
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from madr.api import app
from madr.errors import HttpError
from tests.utils import randstr


class TestHttpErrorHandler:
    @pytest.mark.parametrize('status_code', [HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND])
    def test_http_error_handler(self, client: TestClient, status_code: HTTPStatus) -> None:
        page = randstr()
        message = randstr()

        class TestError(HttpError):
            @property
            def http_status_code(self) -> HTTPStatus:
                return status_code

            @property
            def message(self) -> str:
                return message

        @app.get(f'/{page}', name=page)
        def test_page() -> None:
            raise TestError

        response = client.get(f'/{page}')

        assert response.status_code == status_code
        assert response.json() == {'message': message}

        app.router.routes = [route for route in app.routes if not isinstance(route, APIRoute) or route.name != page]


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
