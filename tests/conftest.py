from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from madr.api import app


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as client:
        yield client
