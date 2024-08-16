from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from madr.settings import Settings

engine = create_engine(Settings().DATABASE_URL.unicode_string())


def get_dbsession() -> Generator[Session]:
    with Session(engine) as session:
        yield session


T_DbSession = Annotated[Session, Depends(get_dbsession)]
