import logging.config
import asyncio
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.cruds import create_db_tables_if_not_exists
from kafka_app.publishers import faststream_app
from api.routers.applications import router as applications_router

logger = logging.getLogger(__name__)
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logging.getLogger('sqlalchemy.engine').propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    await create_db_tables_if_not_exists()
    logger.info("Database tables created successfully.")

    async with faststream_app.lifespan_context():
        yield

    logger.info("Shutting down the application...")


app = FastAPI(
    title="Applications API",
    description="API for managing applications with Kafka integration",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(applications_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Applications API is running!", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


async def main():
    logger.info("Starting Applications API server...")
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        reload=True,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
