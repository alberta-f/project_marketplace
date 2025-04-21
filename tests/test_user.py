import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import config
from app.main import app


async def _auth_client():
    client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
    data = {
        'email': 'testuser@example.com',
        'username': 'tester',
        'password': 'password123',
    }

    response = await client.post('/users/register', json=data)
    assert response.status_code == 200
    resp_data = response.json()
    assert 'id' in resp_data
    assert resp_data['email'] == 'testuser@example.com'

    data = {
        'email': 'testuser@example.com',
        'password': 'password123',
    }

    response = await client.post('/users/auth', json=data)
    assert response.status_code == 200

    response = await client.post('/users/me')
    assert response.status_code == 200
    return client


@pytest.mark.asyncio
async def test_dupl_register():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        data = {
            'email': 'testuser@example.com',
            'username': 'tester',
            'password': 'password1234',
        }
        response = await client.post('/users/register', json=data)

        assert response.status_code == 400
        assert "User already exists" in response.text


@pytest.mark.asyncio
async def test_login_error():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        data_incorrect = {
            'email': 'testuser@example.com',
            'password': 'password1234',
        }

        response = await client.post('/users/login', json=data_incorrect)

        assert response.status_code == 401

        assert 'Invalid email or password' in response.text
        assert config.session.cookie_name not in response.cookies

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        data_correct = {
            'email': 'testuser@example.com',
            'password': 'password123',
        }

        response = await client.post('/users/login', json=data_correct)

        assert response.status_code == 200
        resp_data = response.json()

        assert resp_data['message'] == 'Login successful'
        assert 'user_id' in resp_data
        assert config.session.cookie_name in response.cookies

        return resp_data['user_id']


@pytest.mark.asyncio
async def test_me():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        data_correct = {
            'email': 'testuser@example.com',
            'password': 'password123',
        }

        response_1 = await client.post('/users/login', json=data_correct)
        assert config.session.cookie_name in response_1.cookies

        token = response_1.cookies.get('auth_token')
        assert token is not None

        response_2 = await client.get('/users/me')
        assert response_2.json() == {}

@pytest.mark.asyncio
async def test_logout():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.post('users/logout')
        assert config.session.cookie_name not in response.cookies
