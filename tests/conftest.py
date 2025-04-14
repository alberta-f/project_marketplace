import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.main import app

DATABASE_URL='postgresql+asyncpg://test_user:test_pass@postgres_test:5432/test_db'

engine = create_async_engine(DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(autouse=True)
async def clean_database():
    async with test_session_maker() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

@pytest.fixture(autouse=True)
def mock_minio(monkeypatch):
    def fake_upload_image(self, *args, **kwargs):
        return "https://fake-bucket.test/fake-image.jpg"

    monkeypatch.setattr("app.services.article.MinioService.upload_image", fake_upload_image)


@pytest.fixture(autouse=True)
def mock_email_task(monkeypatch):
    def fake_delay(self, *args, **kwargs):
        pass
    monkeypatch.setattr("app.tasks.email.send_email_task.delay", fake_delay())

@pytest.fixture()
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture()
async def test_user(async_client):
    data = {
        "email": "testuser@example.com",
        "password": "password123",
        "username": "Testy Tester"
    }
    response = await async_client.post("/users/register", json=data)
    assert response.status_code == 201
    return data

@pytest.fixture()
async def authenticated_client(test_user):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/users/login", data={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        assert response.status_code == 200
        client.cookies = response.cookies
        yield client
