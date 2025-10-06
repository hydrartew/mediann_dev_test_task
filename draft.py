import asyncio
import datetime
import json
import logging
import os

from typing import List, Optional

import asyncpg
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from dishka import Provider, Scope, provide, make_async_container
from dishka.integrations.fastapi import inject
from faststream import FastStream
from faststream.kafka import KafkaBroker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "new_applications")

# --- Models ---

class ApplicationCreate(BaseModel):
    user_name: str = Field(..., description="Имя пользователя")
    description: str = Field(..., description="Описание заявки")


class Application(BaseModel):
    id: int
    user_name: str
    description: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Database Setup ---

async def create_db_pool():
    """Creates a PostgreSQL connection pool."""
    try:
        pool = await asyncpg.create_pool(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            min_size=1,  # Minimal number of connections in the pool
            max_size=10  # Maximal number of connections in the pool
        )
        logging.info("Connected to PostgreSQL")
        return pool
    except Exception as e:
        logging.error(f"Error connecting to PostgreSQL: {e}")
        raise


# --- Kafka Setup ---

broker = KafkaBroker(KAFKA_BROKER_URL)
app = FastAPI(lifespan=broker.lifespan_context())
faststream = FastStream(broker)

@broker.publisher(topic=KAFKA_TOPIC)
async def publish_application(application: Application):
    """Publishes application data to Kafka."""
    logging.info(f"Publishing to Kafka: {application.json()}")
    return application.json().encode("utf-8")


# --- Dependency Injection Setup with Dishka ---

class AppProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_db_pool(self) -> asyncpg.Pool:
        return await create_db_pool()

    @provide(scope=Scope.REQUEST)
    def get_transaction(self, pool: asyncpg.Pool) -> asyncpg.Connection:
        return pool.connection() # type: ignore


container = make_async_container(AppProvider())


# --- API Endpoints ---

@app.post("/applications", response_model=Application)
@inject
async def create_application(
    application_create: ApplicationCreate,
    pool: asyncpg.Pool = Depends(lambda: container.get(asyncpg.Pool)),
):
    """Creates a new application."""
    try:
        async with pool.acquire() as conn:
            application = await create_application_db(application_create, conn)
            await publish_application(application)
            return application
    except Exception as e:
        logging.exception("Error creating application")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/applications", response_model=List[Application])
@inject
async def get_applications(
    user_name: Optional[str] = Query(None, description="Фильтр по имени пользователя"),
    page: int = Query(1, description="Номер страницы"),
    size: int = Query(10, description="Размер страницы"),
    pool: asyncpg.Pool = Depends(lambda: container.get(asyncpg.Pool)),
):
    """Retrieves a list of applications with filtering and pagination."""
    try:
        async with pool.acquire() as conn:
             return await list_applications_db(user_name, page, size, conn)
    except Exception as e:
        logging.exception("Error retrieving applications")
        raise HTTPException(status_code=500, detail=str(e))


# --- Database Interactions ---

async def create_application_db(application_create: ApplicationCreate, conn: asyncpg.Connection) -> Application:
    """Creates a new application in the database."""
    try:
        stmt = await conn.prepare("""
            INSERT INTO applications (user_name, description, created_at)
            VALUES ($1, $2, $3)
            RETURNING id, user_name, description, created_at
        """)
        row = await stmt.fetchrow(
            application_create.user_name,
            application_create.description,
            datetime.datetime.utcnow()
        )

        if row:
             return Application(**row)
        else:
            raise HTTPException(status_code=500, detail="Failed to create application in the database")

    except Exception as e:
        logging.error(f"Database error creating application: {e}")
        raise


async def list_applications_db(user_name: Optional[str], page: int, size: int, conn: asyncpg.Connection) -> List[Application]:
    """Retrieves a list of applications from the database with filtering and pagination."""
    try:
        offset = (page - 1) * size
        query = """
            SELECT id, user_name, description, created_at
            FROM applications
        """
        conditions = []
        params = []

        if user_name:
            conditions.append("user_name = $1")
            params.append(user_name)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT $2 OFFSET $3"
        params.extend([size, offset])

        stmt = await conn.prepare(query)
        rows = await stmt.fetch(*params)

        return [Application(**row) for row in rows]
    except Exception as e:
        logging.error(f"Database error listing applications: {e}")
        raise



@app.on_event("startup")
async def startup_event():
    """Creates the applications table if it doesn't exist."""
    try:
        pool = await create_db_pool()  # Ensure the pool is created
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
                )
            """)
        logging.info("Database table 'applications' created or already exists.")
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        raise
    finally:
        if 'pool' in locals():
            await pool.close()




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
