from pydantic.networks import MultiHostUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    DATABASE_URL: PostgresDsn = MultiHostUrl('postgresql+psycopg://postgres:postgres@127.0.0.1:5432/madr')
