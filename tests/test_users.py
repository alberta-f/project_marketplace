import pytest


@pytest.mark.asyncio
async def test_user_registration(test_user):
    assert test_user["email"] == "testuser@example.com"

@pytest.mark.asyncio
async def test_user_login(async_client, test_user):
    response = await async_client.post("/users/login", data={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_users_me(authenticated_client):
    response = await authenticated_client.get("/users/me")
    assert response.status_code == 200
    assert "email" in response.json()
