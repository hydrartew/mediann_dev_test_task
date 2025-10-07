import logging

import asyncio
from typing import Optional

from faststream import FastStream
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka import AIOKafkaProducer

from .broker import broker
from config_reader import settings
from schemas import Application


logger = logging.getLogger(__name__)

faststream_app = FastStream(broker)


_producer: Optional[AIOKafkaProducer] = None
_topic_ready: bool = False


async def _ensure_kafka_topic_once() -> None:
    global _topic_ready
    if _topic_ready:
        return
    admin = AIOKafkaAdminClient(bootstrap_servers=settings.KAFKA_BROKER_URL)
    try:
        await admin.start()
        existing_topics = await admin.list_topics()
        if settings.KAFKA_TOPIC not in existing_topics:
            await admin.create_topics([
                NewTopic(name=settings.KAFKA_TOPIC, num_partitions=1, replication_factor=1)
            ])
            logger.info(f"Created Kafka topic '{settings.KAFKA_TOPIC}'")
        for _ in range(10):
            topics = await admin.list_topics()
            if settings.KAFKA_TOPIC in topics:
                _topic_ready = True
                break
            await asyncio.sleep(0.3)
        if not _topic_ready:
            logger.warning(f"Kafka topic '{settings.KAFKA_TOPIC}' not visible after creation attempts")
    except Exception as e:
        logger.warning(f"Kafka topic ensure failed: {e}")
    finally:
        await admin.close()


async def _get_or_create_producer(start_if_needed: bool = True) -> Optional[AIOKafkaProducer]:
    global _producer
    if _producer is not None:
        return _producer
    if not start_if_needed:
        return None
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BROKER_URL)
    await producer.start()
    _producer = producer
    return _producer


@faststream_app.on_startup
async def kafka_start() -> None:
    await _ensure_kafka_topic_once()
    await _get_or_create_producer(start_if_needed=True)


@faststream_app.on_shutdown
async def kafka_stop() -> None:
    global _producer
    if _producer is not None:
        try:
            await _producer.stop()
        finally:
            _producer = None


async def publish_application(application: Application):
    await _ensure_kafka_topic_once()
    payload_bytes = application.model_dump_json().encode("utf-8")
    logger.info(f"Publishing application to Kafka: {application.model_dump_json()}")

    # Prefer shared producer started via FastStream lifespan
    producer = await _get_or_create_producer(start_if_needed=False)
    if producer is not None:
        await producer.send_and_wait(settings.KAFKA_TOPIC, payload_bytes)
        return payload_bytes

    # Fallback: create a short-lived producer if lifespan isn't active
    temp_producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BROKER_URL)
    try:
        await temp_producer.start()
        await temp_producer.send_and_wait(settings.KAFKA_TOPIC, payload_bytes)
    finally:
        await temp_producer.stop()
    return payload_bytes
