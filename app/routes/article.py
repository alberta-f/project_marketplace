from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.dependencies import get_article_service, get_user_service
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from app.services.article import ArticleService
from app.services.user import UserService

router = APIRouter(prefix="/article", tags=["Article"])


@router.post("/new", response_model=ArticleRead, status_code=201)
async def create_article(
    request: Request,
    data: ArticleCreate = Depends(),
    image: UploadFile | None = File(None),
    user_service: UserService = Depends(get_user_service),
    article_service: ArticleService = Depends(get_article_service),
):
    user = await user_service.get_user_from_cookie(request)

    image_bytes = await image.read() if image else None
    filename = image.filename if image else None

    return await article_service.create(data, user.id, image_bytes, filename)


@router.get("/all", response_model=list[ArticleRead])
async def list_articles(
    article_service: ArticleService = Depends(get_article_service),
):
    return await article_service.list()


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(
    article_id: UUID,
    article_service: ArticleService = Depends(get_article_service),
):
    return await article_service.get(article_id)


@router.put("/{article_id}", response_model=ArticleRead)
async def update_article(
    article_id: UUID,
    data: ArticleUpdate,
    image: UploadFile | None = File(None),
    article_service: ArticleService = Depends(get_article_service),
):
    image_bytes = await image.read() if image else None
    filename = image.filename if image else None

    return await article_service.update(article_id, data, image_bytes, filename)


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: UUID,
    article_service: ArticleService = Depends(get_article_service),
):
    await article_service.delete(article_id)
