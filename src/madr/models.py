from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship


class TimestampMixin(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column(init=False, repr=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, repr=False, server_default=func.now(), onupdate=func.now()
    )


class Base(DeclarativeBase, MappedAsDataclass): ...


class User(TimestampMixin, Base, kw_only=True):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]


class Romancista(TimestampMixin, Base, kw_only=True):
    __tablename__ = 'romancistas'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(unique=True)

    livros: Mapped[list['Livro']] = relationship(
        back_populates='romancista', cascade='all, delete-orphan', init=False, repr=False
    )


class Livro(TimestampMixin, Base, kw_only=True):
    __tablename__ = 'livros'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(unique=True)
    year: Mapped[int]
    romancista_id: Mapped[int] = mapped_column(ForeignKey('romancistas.id'), init=False)
    romancista: Mapped['Romancista'] = relationship(back_populates='livros', repr=False)
