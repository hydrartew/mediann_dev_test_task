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

from config_reader import settings


broker = KafkaBroker()
app = FastAPI(lifespan=broker.lifespan_context())
faststream = FastStream(broker)

@broker.publisher(topic=settings.KAFKA_TOPIC)
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
