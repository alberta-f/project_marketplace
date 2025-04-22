from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Request

from app.dependencies import get_article_service
from app.routes.utils.cookie import get_user_from_cookie
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from app.services.article import ArticleService

router = APIRouter(prefix="/article", tags=["Article"])


@router.post("/", response_model=ArticleRead, status_code=201)
async def create_article(
    request: Request,
    data: ArticleCreate = Depends(ArticleCreate.as_form),
    image_bytes: bytes = File(None),
    article_service: ArticleService = Depends(get_article_service),
):
    user = get_user_from_cookie(request)

    return await article_service.create(data, user.id, image_bytes)


@router.get("/", response_model=list[ArticleRead])
async def list_articles(
    search: str | None = Query(None),
    category_id: UUID | None = Query(None),
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    article_service: ArticleService = Depends(get_article_service),
):
    return await article_service.list_paginated(search, category_id, page_number, page_size)


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(
    article_id: UUID,
    article_service: ArticleService = Depends(get_article_service),
):
    return await article_service.get(article_id)


@router.get("/users/me", response_model=list[ArticleRead])
async def current_user_articles(
    request: Request,
    article_service: ArticleService = Depends(get_article_service)
):
    user = get_user_from_cookie(request)
    return await article_service.get_articles_by_user_id(user.id)


@router.get("/users/{user_id}", response_model=list[ArticleRead])
async def user_articles(
    user_id: UUID,
    article_service: ArticleService = Depends(get_article_service),
):
    return await article_service.get_articles_by_user_id(user_id)




@router.put("/{article_id}", response_model=ArticleRead)
async def update_article(
    request: Request,
    article_id: UUID,
    data: ArticleUpdate = Depends(ArticleUpdate.as_form),
    image_bytes: bytes = File(None),
    article_service: ArticleService = Depends(get_article_service),
):
    user = get_user_from_cookie(request)

    return await article_service.update(article_id=article_id,
                                        data=data,
                                        user_id=user.id,
                                        image_bytes=image_bytes,)

@router.delete("/{article_id}", status_code=204)
async def delete_article(
    request: Request,
    article_id: UUID,
    article_service: ArticleService = Depends(get_article_service),
):
    user = get_user_from_cookie(request)

    await article_service.delete(article_id, user.id)
