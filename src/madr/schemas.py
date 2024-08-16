from pydantic import BaseModel


class Message(BaseModel):
    message: str


class ApiInfo(BaseModel):
    name: str
    description: str
    version: str
