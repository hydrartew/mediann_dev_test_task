import json
import pytest

from kafka_app.publishers import publish_application
from schemas import Application


@pytest.mark.asyncio
async def test_publish_application_uses_producer(monkeypatch):
    sent = {}

    class DummyProducer:
        async def start(self):
            return None

        async def stop(self):
            return None

        async def send_and_wait(self, topic, payload):
            sent["topic"] = topic
            sent["payload"] = json.loads(payload.decode("utf-8"))

    async def fake_startup():
        return None

    import kafka_app.publishers as mod

    def fake_new_producer(*args, **kwargs):
        return DummyProducer()

    monkeypatch.setattr(mod, "AIOKafkaProducer", fake_new_producer)

    app_model = Application(id=1, user_name="alice", description="hi", created_at="2025-01-01T00:00:00Z")
    await publish_application(app_model)

    assert sent["topic"] is not None
    assert sent["payload"]["user_name"] == "alice"
