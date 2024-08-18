from madr.security import get_password_hash, verify_password
from tests.utils import randstr


class TestPasswordHash:
    def test_password(self) -> None:
        password = randstr()

        hash_ = get_password_hash(password)

        assert verify_password(password, hash_)

    def test_invalid_password(self) -> None:
        password = randstr()

        hash_ = get_password_hash(password)

        assert not verify_password(password + '0', hash_)
