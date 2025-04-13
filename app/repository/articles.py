from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article
from app.repository.db_base import DBRepository


class ArticleRepository(DBRepository[Article]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Article)

    async def get_by_id(self, id: UUID) -> Article | None:
        result = await self.db.execute(
            select(Article)
            .where(Article.id == id)
            .where(Article.deleted is False)
            .options(selectinload(Article.categories))  # уже было
        )
        return result.scalar_one_or_none()


    async def get_paginated(self,
                            search: str | None,
                            category_id: UUID | None,
                            page: int,
                            size: int):
        stmt = select(Article).where(Article.deleted is False)

        if search:
            stmt = stmt.where(
                text("to_tsvector('russian', title || ' ' || content) @@ plainto_tsquery(:query)")
            ).params(query=search)

        if category_id:
            stmt = stmt.where(Article.category_id == category_id)

        stmt = stmt.offset((page - 1) * size).limit(size)

        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def get_articles_by_user_id(self, user_id):
        result = await self.db.execute(
            select(Article)
            .where(Article.author_id == user_id)
            .where(Article.deleted is False)
            .options(selectinload(Article.categories))
        )
        result = result.scalars()
        return result.all()

    async def delete(self, article: Article):
        article.deleted = True
        await self.db.commit()
        await self.db.refresh(article)
