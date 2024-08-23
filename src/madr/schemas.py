from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, PositiveInt, field_validator

from .security import get_password_hash
from .utils import sanitize


class NoArgs(Enum):
    NO_ARG = 0


NO_ARG = NoArgs.NO_ARG


class Message(BaseModel):
    message: str


class ApiInfo(BaseModel):
    name: str
    description: str
    version: str


class Token(BaseModel):
    token_type: Literal['bearer'] = 'bearer'
    access_token: str


class UserSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

    @field_validator('username')
    @classmethod
    def username_validate(cls, v: str) -> str:
        v = sanitize(v)
        if not v:
            raise ValueError('username não deve estar em branco')
        return v

    @field_validator('password')
    @classmethod
    def password_validate(cls, v: str) -> str:
        return get_password_hash(v)


class UserPublic(BaseModel):
    model_config = {'from_attributes': True}

    id: int
    email: EmailStr
    username: str


class RomancistaSchema(BaseModel):
    name: str = Field(min_length=1)

    @field_validator('name')
    @classmethod
    def name_validate(cls, v: str) -> str:
        v = sanitize(v)
        if not v:
            raise ValueError('name não deve estar em branco')
        return v


class RomancistaPublic(BaseModel):
    model_config = {'from_attributes': True}

    id: int
    name: str


class RomancistaList(BaseModel):
    romancistas: list[RomancistaPublic]


class LivroSchema(BaseModel):
    title: str = Field(min_length=1)
    year: PositiveInt
    romancista_id: int

    @field_validator('title')
    @classmethod
    def title_validate(cls, v: str) -> str:
        v = sanitize(v)
        if not v:
            raise ValueError('title não deve estar em branco')
        return v


class LivroPatch(BaseModel):
    title: str | NoArgs = Field(NO_ARG, min_length=1)
    year: PositiveInt | NoArgs = NO_ARG
    romancista_id: int | NoArgs = NO_ARG

    @field_validator('title')
    @classmethod
    def title_validate(cls, v: str) -> str:
        v = sanitize(v)
        if not v:
            raise ValueError('title não deve estar em branco')
        return v


class LivroPublic(BaseModel):
    model_config = {'from_attributes': True}

    id: int
    title: str
    year: int
    romancista_id: int


class LivroList(BaseModel):
    livros: list[LivroPublic]
