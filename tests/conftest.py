import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import get_db
from app.main import app
from app.models import Base
from app.services.minio import MinioService
from app.tasks.email import send_email_task

DATABASE_URL = 'postgresql+asyncpg://test_user:test_pass@postgres_test:5432/test_db'


engine = create_async_engine(DATABASE_URL, echo=False)
SessionTest = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope='session', autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def session():
    async with SessionTest() as session:
        yield session


@pytest.fixture
async def client(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
        yield c


@pytest.fixture(autouse=True)
def override_celery_task(monkeypatch):
    monkeypatch.setattr(send_email_task, 'delay', lambda *args, **kwargs: None)


@pytest.fixture(autouse=True)
def override_upload_image(monkeypatch):
    monkeypatch.setattr(MinioService, 'upload_image', lambda *args, **kwargs: None)
