import logging

# import asyncio

from sqlalchemy import select, func, column
from sqlalchemy.dialects.postgresql import insert

from db.base import async_session_factory, Base, async_engine
from db.models import ApplicationTable
from utils import async_retry_settings

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

# @async_retry_settings()
# def add_row_posts_to_db(list_posts: list[Post] | ListPosts) -> None:
#     logger.info(f'Attempting to add/update {len(list_posts)} posts.')

#     try:

#         with session_factory() as session:
#             for p in list_posts:
#                 stmt = insert(RawPostsTable).values(
#                     id=p.id,
#                     user_id=p.user_id,
#                     title=p.title,
#                     body=p.body
#                 )

#                 do_update_stmt = stmt.on_conflict_do_update(
#                     index_elements=[RawPostsTable.id],
#                     set_=dict(title=p.title, body=p.body)
#                 )

#                 session.execute(do_update_stmt)

#             session.commit()
#             logger.info(f'Posts were added/updated successfully.')

#     except Exception:
#         logger.error('Error adding posts. Traceback below in the log.')
#         if session:
#             logger.info('Rollback add_posts session.')
#             session.rollback()
#         raise


# @retry_settings()
# def collect_top_users() -> None:
#     logger.info('Calculating top users by posts.')

#     try:
#         with session_factory() as session:
#             subquery = (
#                 select(
#                     RawPostsTable.user_id,
#                     func.count().label('posts_cnt')
#                 )
#                 .group_by(RawPostsTable.user_id)
#                 .order_by(column('posts_cnt').desc(), column('user_id'))
#             )

#             stmt = insert(TopUsersTable).from_select(
#                 ['user_id', 'posts_cnt'],
#                 select(
#                     subquery.c.user_id,
#                     subquery.c.posts_cnt
#                 )
#             )

#             do_update_stmt = stmt.on_conflict_do_update(
#                 index_elements=[TopUsersTable.user_id],
#                 set_=dict(
#                     posts_cnt=stmt.excluded.posts_cnt,
#                     calculated_at=func.now()
#                 )
#             )

#             session.execute(do_update_stmt)

#             session.commit()
#             logger.info('Top users calculated and updated successfully.')

#     except Exception:
#         logger.error('Error calculating top users. Traceback below in the log.')
#         if session:
#             logger.info('Rollback add_posts session.')
#             session.rollback()
#         raise


# @retry_settings()
# def get_all_top_users() -> list[TopUsersTable]:
#     logger.info('Fetching all top users from the database.')

#     try:
#         with session_factory() as session:
#             stmt = select(TopUsersTable)
#             result = session.execute(stmt)
#             top_users = result.scalars().all()

#             logger.info(f'Successfully fetched {len(top_users)} top users.')

#             return list(top_users)

#     except Exception as e:
#         logger.error(f'Error fetching top users: {e}. Traceback below in the log.')
#         if 'session' in locals() and session:
#             logger.info('Rollback get_all_top_users session (if applicable).')
#             session.rollback()
#         raise
