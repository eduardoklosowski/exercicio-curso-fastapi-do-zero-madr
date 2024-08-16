import pytest
import sqlalchemy as sa

from madr.database import get_dbsession


class TestGetSession:
    def test_run(self, dbengine: sa.Engine) -> None:
        returned = get_dbsession()
        session = next(returned)
        with pytest.raises(StopIteration):
            next(returned)

        assert session.execute(sa.select(sa.text('1 + 1'))).one() == (2,)
