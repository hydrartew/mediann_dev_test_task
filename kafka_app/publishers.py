import logging

from faststream import FastStream

from .broker import broker
from config_reader import settings
from schemas import Application


logger = logging.getLogger(__name__)

faststream_app = FastStream(broker)


@broker.publisher(topic=settings.KAFKA_TOPIC)
async def publish_application(application: Application):
    logger.info(f"Publishing application to Kafka: {application.model_dump_json()}")
    return application.model_dump_json().encode("utf-8")
