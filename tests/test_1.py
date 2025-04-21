import pytest
from httpx import ASGITransport, AsyncClient

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
async def test_update_and_delete():
    client = await _auth_client()

    try:
        new_username = 'rename'
        response = await client.put('/users/me', json={'username': new_username})
        assert response.status_code == 204

    finally:
        await client.aclose()
