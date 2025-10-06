from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config_reader import settings

db_host = settings.POSTGRES_HOST
db_port = settings.POSTGRES_PORT
db_name = settings.POSTGRES_DB
db_user = settings.POSTGRES_USER
db_password = settings.POSTGRES_PASSWORD.get_secret_value()

db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

async_engine = create_async_engine(
    db_url,
    echo=settings.SQLALCHEMY_ECHO_FLAG
)

async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
