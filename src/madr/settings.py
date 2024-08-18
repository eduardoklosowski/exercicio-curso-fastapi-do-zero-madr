from pydantic.networks import MultiHostUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    SECRET_KEY: str
    DATABASE_URL: PostgresDsn = MultiHostUrl('postgresql+psycopg://postgres:postgres@127.0.0.1:5432/madr')
    ACCESS_TOKEN_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
