import pytest


@pytest.mark.asyncio
async def test_register(async_client):
    response = await async_client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"

async def test_login(async_client, inactive_user, active_user):
    response = await async_client.post("/auth/login", json=inactive_user)
    assert response.status_code == 403

    response = await async_client.post('/auth/login', json=active_user)
    assert response.status_code == 200
