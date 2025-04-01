import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import tasks
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.models.models import User
from app.services import jwt

# ⚠️ Новый движок SQLite (in-memory)
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DB_URL, echo=True)
async_session_test_ = async_sessionmaker(engine_test, expire_on_commit=False)

# ⚡ Переопределим зависимость
app.dependency_overrides[get_db_session] = lambda: async_session_test()


@pytest.fixture(scope='session')
def async_session_test():
    return async_session_test_


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def mock_tasks(monkeypatch):
    class FakeTask:
        def delay(self, *args, **kwargs):
            pass

    monkeypatch.setattr(tasks.email, "send_email_task", FakeTask())


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    async def fake_store_token(*args, **kwargs):
        pass

    async def fake_delete_token(*args, **kwargs):
        pass

    async def fake_delete_all_user_access_tokens(*args, **kwargs):
        pass

    monkeypatch.setattr(jwt, "store_token", fake_store_token)
    monkeypatch.setattr(jwt, "delete_token", fake_delete_token)
    monkeypatch.setattr(jwt, "delete_all_user_access_tokens", fake_delete_all_user_access_tokens)


@pytest.fixture
async def async_client():
    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app=app)  # 💡 это ключ
    ) as client:
        yield client


@pytest.fixture
async def inactive_user(async_client):
    data = {
        "email": "inactive@example.com",
        "username": "inactive_user",
        "password": "testpass123"
    }
    await async_client.post("/auth/register", json=data)
    return data

@pytest.fixture
async def active_user(async_client, async_session_test):
    data = {
        "email": "active@example.com",
        "username": "active_user",
        "password": "testpass123"
    }
    await async_client.post("/auth/register", json=data)

    # Активируем через БД
    await async_session_test.execute(
        update(User).where(User.email == data["email"]).values(is_active=True)
    )
    await async_session_test.commit()

    return data
