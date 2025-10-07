import os
import sys
from pathlib import Path
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session", autouse=True)
def set_test_env() -> None:
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")
    os.environ.setdefault("POSTGRES_DB", "test_db")
    os.environ.setdefault("POSTGRES_USER", "test_user")
    os.environ.setdefault("POSTGRES_PASSWORD", "test_pass")
    os.environ.setdefault("KAFKA_BROKER_URL", "localhost:9092")
    os.environ.setdefault("KAFKA_TOPIC", "applications_test")


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
