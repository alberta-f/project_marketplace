from uuid import UUID

from sqlalchemy import select
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
            .options(selectinload(Article.categories))  # уже было
        )
        return result.scalar_one_or_none()

    async def soft_delete(self, obj: Article):
        obj.deleted = True
        await self.db.commit()

    async def get_all(self, with_deleted: bool = False):
        stmt = select(Article)

        if not with_deleted:
            stmt = stmt.where(Article.deleted.is_(False))

        result = await self.db.scalars(stmt)
        return result.all()
