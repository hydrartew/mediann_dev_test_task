import logging

from sqlalchemy import select

from db.base import async_session_factory, Base, async_engine
from db.models import ApplicationTable
from schemas import ApplicationCreate

logger = logging.getLogger(__name__)


async def create_db_tables_if_not_exists(drop_all: bool = False) -> None:
    try:
        if drop_all:
            logger.info('Attempting to drop all tables, if they exist.')
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info('Database tables dropped successfully.')

        logger.info('Creating new tables if not exists.')
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info('Tables already exist or created successfully.')

    except Exception as e:
        logger.error(f'Error dropping or/and creating database tables: {e}', exc_info=True)


async def create_application(data: ApplicationCreate) -> ApplicationTable:
    try:
        async with async_session_factory() as session:
            application = ApplicationTable(
                user_name=data.user_name,
                description=data.description
            )
            session.add(application)
            await session.commit()
            await session.refresh(application)
            logger.info(f'Application created successfully with ID: {application.id}')
            return application
    except Exception as e:
        logger.error(f'Error creating application: {e}', exc_info=True)
        raise


async def get_application_by_id(application_id: int) -> ApplicationTable | None:
    try:
        async with async_session_factory() as session:
            stmt = select(ApplicationTable).where(ApplicationTable.id == application_id)
            result = await session.execute(stmt)
            application = result.scalar_one_or_none()
            return application
    except Exception as e:
        logger.error(f'Error getting application by ID {application_id}: {e}', exc_info=True)
        raise


async def get_all_applications(limit: int = 100, offset: int = 0) -> list[ApplicationTable]:
    try:
        async with async_session_factory() as session:
            stmt = select(ApplicationTable).offset(offset).limit(limit).order_by(ApplicationTable.created_at.desc())
            result = await session.execute(stmt)
            applications = result.scalars().all()
            logger.info(f'Retrieved {len(applications)} applications')
            return list(applications)
    except Exception as e:
        logger.error(f'Error getting applications: {e}', exc_info=True)
        raise


async def get_applications_by_user_name(user_name: str, limit: int = 100, offset: int = 0) -> list[ApplicationTable]:
    try:
        async with async_session_factory() as session:
            stmt = (
                select(ApplicationTable)
                .where(ApplicationTable.user_name == user_name)
                .offset(offset)
                .limit(limit)
                .order_by(ApplicationTable.created_at.desc())
            )
            result = await session.execute(stmt)
            applications = result.scalars().all()
            logger.info(f'Retrieved {len(applications)} applications for user {user_name}')
            return list(applications)
    except Exception as e:
        logger.error(f'Error getting applications by user name {user_name}: {e}', exc_info=True)
        raise
