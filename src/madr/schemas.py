from pydantic import BaseModel


class ApiInfo(BaseModel):
    name: str
    description: str
    version: str
