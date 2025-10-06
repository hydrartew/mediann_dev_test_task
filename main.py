import logging.config
import asyncio
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.cruds import create_db_tables_if_not_exists
from api.routers.applications import router as applications_router

logger = logging.getLogger(__name__)
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logging.getLogger('sqlalchemy.engine').propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    await create_db_tables_if_not_exists()
    logger.info("Database tables created successfully.")
    
    yield
    
    logger.info("Shutting down the application...")


app = FastAPI(
    title="Applications API",
    description="API for managing applications with Kafka integration",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        port=8000,
        reload=True,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
