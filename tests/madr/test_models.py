from random import randint

from sqlalchemy.orm import Session

from tests.factories import LivroFactory, RomancistaFactory


class TestRomancista:
    def test_livros(self, dbsession: Session) -> None:
        romancista = RomancistaFactory.build()
        dbsession.add(romancista)
        dbsession.commit()

        livros = LivroFactory.build_batch(randint(3, 10), romancista=romancista)
        dbsession.add_all(livros)
        dbsession.commit()

        assert romancista.livros == livros


class TestLivros:
    def test_romancista(self, dbsession: Session) -> None:
        romancista = RomancistaFactory.build()
        dbsession.add(romancista)
        dbsession.commit()

        livro = LivroFactory.build(romancista=romancista)
        dbsession.add(livro)
        dbsession.commit()

        assert livro.romancista == romancista
