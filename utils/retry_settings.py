import logging

from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, before_sleep_log

logger = logging.getLogger(__name__)


def async_retry_settings():
    return AsyncRetrying(
        stop=stop_after_attempt(5),
        wait=wait_exponential(min=1, max=4),
        before_sleep=before_sleep_log(logger, logging.INFO, exc_info=True)
    )
