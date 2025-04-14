import pytest


@pytest.mark.asyncio
async def test_create_category(authenticated_client):
    response = await authenticated_client.post("/categories/", json={"title": "Test Category"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Category"
    assert "id" in data
