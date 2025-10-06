import logging.config
import asyncio

from config_reader import settings
from db.cruds import create_db_tables_if_not_exists

logger = logging.getLogger(__name__)
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logging.getLogger('sqlalchemy.engine').propagate = False


async def main():
    await create_db_tables_if_not_exists()


if __name__ == '__main__':
    asyncio.run(main())
