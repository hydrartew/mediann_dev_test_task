import json
import pytest
import httpx
from httpx import ASGITransport

from main import app


@pytest.mark.asyncio
async def test_create_application_publishes_kafka(monkeypatch):
    published = {}

    async def fake_publish(app_model):
        published["payload"] = json.loads(app_model.model_dump_json())
        return b"ok"

    class FakeDBApp:
        id = 1
        user_name = "alice"
        description = "hello"
        created_at = "2025-01-01T00:00:00Z"

    async def fake_create(data):
        return FakeDBApp

    monkeypatch.setattr("api.routers.applications.publish_application", fake_publish)
    monkeypatch.setattr("api.routers.applications.create_application", fake_create)

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/applications",
            json={"user_name": "alice", "description": "hello"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["user_name"] == "alice"
    assert body["description"] == "hello"
    assert "payload" in published
    assert published["payload"]["user_name"] == "alice"


@pytest.mark.asyncio
async def test_get_applications(monkeypatch):
    class Obj:
        id = 1
        user_name = "bob"
        description = "desc"
        created_at = "2025-01-01T00:00:00Z"

    async def fake_all(limit: int, offset: int):
        return [Obj]

    monkeypatch.setattr("api.routers.applications.get_all_applications", fake_all)

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/applications")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["user_name"] == "bob"
