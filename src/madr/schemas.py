from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from .security import get_password_hash
from .utils import sanitize


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
