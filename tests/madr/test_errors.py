from http import HTTPStatus

from madr.errors import ConflictError, InvalidLoginError, NotFoundError, UnauthorizedError
from tests.utils import randstr


class TestInvalidLoginError:
    def test_http_status_code(self) -> None:
        sut = InvalidLoginError()

        assert sut.http_status_code == HTTPStatus.BAD_REQUEST

    def test_message(self) -> None:
        sut = InvalidLoginError()

        assert sut.message == 'Email ou senha incorretos'


class TestUnauthorizedError:
    def test_http_status_code(self) -> None:
        sut = UnauthorizedError()

        assert sut.http_status_code == HTTPStatus.UNAUTHORIZED

    def test_message(self) -> None:
        sut = UnauthorizedError()

        assert sut.message == 'Não autorizado'


class TestNotFoundError:
    def test_http_status_code(self) -> None:
        sut = NotFoundError(resource=randstr())

        assert sut.http_status_code == HTTPStatus.NOT_FOUND

    def test_message(self) -> None:
        resource = randstr()

        sut = NotFoundError(resource=resource)

        assert sut.message == f'{resource} não consta no MADR'


class TestConflictError:
    def test_http_status_code(self) -> None:
        sut = ConflictError(resource=randstr())

        assert sut.http_status_code == HTTPStatus.CONFLICT

    def test_message(self) -> None:
        resource = randstr()

        sut = ConflictError(resource=resource)

        assert sut.message == f'{resource} já consta no MADR'
