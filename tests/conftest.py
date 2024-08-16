from collections.abc import Generator
from urllib.parse import urlparse

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from madr.api import app
from madr.database import get_dbsession
from madr.models import Base
from madr.settings import Settings
from tests.utils import randstr


@pytest.fixture(scope='session')
def dbengine() -> Generator[Engine]:
    database_url = urlparse(Settings().DATABASE_URL.unicode_string())

    main_url = database_url._replace(scheme='postgresql').geturl()
    test_database = f'{database_url.path.removeprefix('/')}_test_{randstr(16).lower()}'
    test_url = database_url._replace(path=test_database).geturl()

    main_conn = psycopg.connect(main_url, autocommit=True)
    main_conn.execute(f'CREATE DATABASE {test_database}')

    yield create_engine(test_url)

    main_conn.execute(f'DROP DATABASE {test_database} WITH (FORCE)')
    main_conn.close()


@pytest.fixture
def dbsession(dbengine: Engine) -> Generator[Session]:
    Base.metadata.create_all(dbengine)

    with Session(dbengine) as session:
        yield session

    Base.metadata.drop_all(dbengine)


@pytest.fixture
def client(dbsession: Session) -> Generator[TestClient]:
    def get_session_override() -> Session:
        return dbsession

    with TestClient(app) as client:
        app.dependency_overrides[get_dbsession] = get_session_override
        yield client

    app.dependency_overrides.clear()
