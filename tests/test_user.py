import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import config
from app.main import app


@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
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
        return resp_data


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
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as client:
        # 1) логинимся
        login_data = {"email": "testuser@example.com", "password": "password123"}
        resp_login = await client.post("/users/login", json=login_data)
        assert resp_login.status_code == 200

        # 2) берём токен из Set‑Cookie
        token = resp_login.cookies[config.session.cookie_name]

        # 3‑а) самый надёжный способ — передать через параметр cookies
        resp_me = await client.get(
            "/users/me",
            cookies={config.session.cookie_name: token},
        )

        # ----- либо -----
        # 3‑б) вбить куку в CookieJar клиента
        # client.cookies.set(config.session.cookie_name, token, path="/")
        # resp_me = await client.get("/users/me")

        assert resp_me.status_code == 200
        assert resp_me.json()["email"] == login_data["email"]

# @pytest.mark.asyncio
# async def test_logout():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
#         response = await client.post('users/logout')
