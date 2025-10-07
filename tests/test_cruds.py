import pytest

from schemas import ApplicationCreate
import db.cruds as cruds


@pytest.mark.asyncio
async def test_create_application_calls_db(monkeypatch):
    class FakeApp:
        id = 123
        user_name = "t1"
        description = "d1"
        created_at = "2025-01-01T00:00:00Z"

    async def fake_create(data: ApplicationCreate):
        return FakeApp

    monkeypatch.setattr(cruds, "create_application", fake_create)

    data = ApplicationCreate(user_name="t1", description="d1")
    created = await cruds.create_application(data)  # using monkeypatched function
    assert created.id == 123
