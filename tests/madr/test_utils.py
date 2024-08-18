import pytest

from madr.utils import sanitize


class TestSanitize:
    @pytest.mark.parametrize(
        ('value', 'expected'),
        [
            ('Machado de Assis', 'machado de assis'),
            ('Manuel        Bandeira', 'manuel bandeira'),
            ('Edgar Alan Poe         ', 'edgar alan poe'),
            ('Androides Sonham Com Ovelhas Elétricas?', 'androides sonham com ovelhas elétricas'),
            ('  breve  história  do tempo ', 'breve história do tempo'),
            ('O mundo assombrado pelos demônios', 'o mundo assombrado pelos demônios'),
        ],
    )
    def test_sanitize_value(self, value: str, expected: str) -> None:
        assert sanitize(value) == expected
