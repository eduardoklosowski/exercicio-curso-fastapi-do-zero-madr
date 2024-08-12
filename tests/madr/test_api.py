from http import HTTPStatus
from importlib.metadata import version

from fastapi.testclient import TestClient


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
