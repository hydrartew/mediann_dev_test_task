from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).parents[0])

    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', extra='allow')

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr

    SQLALCHEMY_ECHO_FLAG: bool = False


settings = Settings()
