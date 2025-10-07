import logging

from faststream.kafka import KafkaBroker

from config_reader import settings


logger = logging.getLogger(__name__)


# Shared Kafka broker instance configured from settings
broker = KafkaBroker(settings.KAFKA_BROKER_URL)


