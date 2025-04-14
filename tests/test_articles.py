import pytest


@pytest.fixture()
async def test_category_id(authenticated_client):
    response = await authenticated_client.post("/categories/", json={"title": "АвтоКатегория"})
    assert response.status_code == 201
    return response.json()["id"]

@pytest.mark.asyncio
async def test_create_article_without_image(authenticated_client, test_category_id):
    response = await authenticated_client.post(
        "/articles/",
        data={
            "title": "Без картинки",
            "content": "Контент",
            "category_ids": [test_category_id]
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Без картинки"

@pytest.mark.asyncio
async def test_create_article_with_image(authenticated_client, test_category_id):
    image_bytes = b"fake-image-content"
    files = {"image_bytes": ("test.jpg", image_bytes, "image/jpeg")}
    data = {
        "title": "С картинкой",
        "content": "Контент",
        "category_ids": [test_category_id]
    }
    response = await authenticated_client.post("/articles/", data=data, files=files)
    assert response.status_code == 201
    assert "image" in response.json()

@pytest.mark.asyncio
async def test_soft_delete_article(authenticated_client, test_category_id):
    create = await authenticated_client.post("/articles/", data={
        "title": "Удалим",
        "content": "Временно",
        "category_ids": [test_category_id]
    })
    article_id = create.json()["id"]
    delete = await authenticated_client.delete(f"/articles/{article_id}")
    assert delete.status_code == 204
    get = await authenticated_client.get(f"/articles/{article_id}")
    assert get.status_code == 404

@pytest.mark.asyncio
async def test_search_articles(authenticated_client, test_category_id):
    await authenticated_client.post("/articles/", data={
        "title": "Ищем это",
        "content": "Ключевое слово",
        "category_ids": [test_category_id]
    })
    resp = await authenticated_client.get("/articles/", params={"search": "ищем"})
    assert resp.status_code == 200
    assert any("Ищем это" in a["title"] for a in resp.json())

@pytest.mark.asyncio
async def test_filter_articles_by_category(authenticated_client, test_category_id):
    await authenticated_client.post("/articles/", data={
        "title": "КатФильтр",
        "content": "Для фильтрации",
        "category_ids": [test_category_id]
    })
    resp = await authenticated_client.get("/articles/", params={"category_id": test_category_id})
    assert resp.status_code == 200
    assert any("КатФильтр" in a["title"] for a in resp.json())

@pytest.mark.asyncio
async def test_article_pagination(authenticated_client, test_category_id):
    for i in range(5):
        await authenticated_client.post("/articles/", data={
            "title": f"Статья {i}",
            "content": "Контент",
            "category_ids": [test_category_id]
        })
    resp = await authenticated_client.get("/articles/", params={"page_number": 1, "page_size": 2})
    assert resp.status_code == 200
    assert len(resp.json()) == 2
