import logging

from faststream.kafka import KafkaBroker

from config_reader import settings


logger = logging.getLogger(__name__)


broker = KafkaBroker(settings.KAFKA_BROKER_URL)
