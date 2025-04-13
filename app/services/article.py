from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.article import ArticleNotFoundException
from app.exceptions.user import NotRootException
from app.models.article import Article
from app.repository.articles import ArticleRepository
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.services.category import CategoryService
from app.services.minio import MinioService


class ArticleService:
    def __init__(
            self,
            db: AsyncSession,
            minio_service: MinioService,
            category_service: CategoryService,
    ):
        self.minio_service = minio_service
        self.category_service = category_service
        self.article_repository = ArticleRepository(db)

    async def create(
        self,
        data: ArticleCreate,
        author_id: UUID,
        image_bytes: bytes | None,
    ) -> Article:
        image_url = None
        if image_bytes:
            image_url = self.minio_service.upload_image(image_bytes)

        data.category_ids = [UUID(category) for category in data.category_ids if category != '']

        article = Article(
            title=data.title,
            content=data.content,
            image=image_url,
            author_id=author_id,
        )

        article.categories = await self.category_service.get_many_by_ids(data.category_ids)

        await self.article_repository.create(article)
        return article


    async def get(self, article_id: UUID) -> Article:
        article = await self.article_repository.get_by_id(article_id)
        if not article or article.deleted:
            raise ArticleNotFoundException()
        return article


    async def list(self) -> list[Article]:
        return await self.article_repository.get_all()


    async def update(
        self,
        article_id: UUID,
        data: ArticleUpdate,
        user_id: UUID,
        image_bytes: bytes | None = None,
    ) -> Article:
        data.category_ids = [UUID(category) for category in data.category_ids if category != '']

        article = await self.article_repository.get_by_id(article_id)

        if article.author_id == user_id:
            await self.article_repository.soft_delete(article)

        article.title = data.title
        article.content = data.content
        article.categories = await self.category_service.get_many_by_ids(data.category_ids)

        if image_bytes:
            article.image = self.minio_service.upload_image(image_bytes)

        await self.article_repository.update(article)
        return article


    async def delete(self, article_id: UUID, user_id: UUID) -> None:
        article = await self.get(article_id)

        if article.author_id == user_id:
            await self.article_repository.delete(article)

        else:
            raise NotRootException()

    async def get_articles_by_user_id(self, user_id: UUID):
        return await self.article_repository.get_articles_by_user_id(user_id)


    async def list_paginated(self,
                             search: str | None,
                             category_id: UUID | None,
                             page: int,
                             size: int):
        return await self.article_repository.get_paginated(search, category_id, page, size)
