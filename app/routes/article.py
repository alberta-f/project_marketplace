from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.dependencies import get_article_service
from app.routes.utils.cookie import get_user_from_cookie
from app.routes.utils.files import get_optional_file, read_optional_file
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from app.services.article import ArticleService

router = APIRouter(prefix="/article", tags=["Article"])


@router.post("/", response_model=ArticleRead, status_code=201)
async def create_article(
    request: Request,
    data: ArticleCreate = Depends(ArticleCreate.as_form),
    image: UploadFile = File(None),
    article_service: ArticleService = Depends(get_article_service),
):
    user = get_user_from_cookie(request)

    image_bytes, filename = await read_optional_file(image)

    return await article_service.create(data, user.id, image_bytes, filename)


@router.get("/all", response_model=list[ArticleRead])
async def list_articles(
    article_service: ArticleService=Depends(get_article_service),
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
    request: Request,
    article_id: UUID,
    data: ArticleUpdate = Depends(ArticleUpdate.as_form),
    image: UploadFile = File(None),
    article_service: ArticleService = Depends(get_article_service),
):
    user = get_user_from_cookie(request)

    image = await get_optional_file(image)

    image_bytes, filename = await read_optional_file(image)
    return await article_service.update(article_id=article_id,
                                        data=data,
                                        user_id=user.id,
                                        image_bytes=image_bytes,
                                        filename=filename)


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    request: Request,
    article_id: UUID,
    article_service: ArticleService = Depends(get_article_service),
):
    user = get_user_from_cookie(request)

    await article_service.delete(article_id, user.id)
