from abc import ABC, abstractmethod
from http import HTTPStatus


class HttpError(ABC, Exception):
    @property
    @abstractmethod
    def http_status_code(self) -> HTTPStatus:
        raise NotImplementedError

    @property
    @abstractmethod
    def message(self) -> str:
        raise NotImplementedError


class InvalidLoginError(HttpError):
    @property
    def http_status_code(self) -> HTTPStatus:
        return HTTPStatus.BAD_REQUEST

    @property
    def message(self) -> str:
        return 'Email ou senha incorretos'


class UnauthorizedError(HttpError):
    @property
    def http_status_code(self) -> HTTPStatus:
        return HTTPStatus.UNAUTHORIZED

    @property
    def message(self) -> str:
        return 'Não autorizado'


class NotFoundError(HttpError):
    def __init__(self, *, resource: str) -> None:
        self.resource = resource

    @property
    def http_status_code(self) -> HTTPStatus:
        return HTTPStatus.NOT_FOUND

    @property
    def message(self) -> str:
        return f'{self.resource} não consta no MADR'


class ConflictError(HttpError):
    def __init__(self, *, resource: str) -> None:
        self.resource = resource

    @property
    def http_status_code(self) -> HTTPStatus:
        return HTTPStatus.CONFLICT

    @property
    def message(self) -> str:
        return f'{self.resource} já consta no MADR'
