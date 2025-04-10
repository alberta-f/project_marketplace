from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.repository.db_base import DBRepository


class ArticleRepository(DBRepository[Article]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Article)

    async def soft_delete(self, obj: Article):
        obj.deleted = True
        await self.db.commit()

    async def get_all(self, with_deleted: bool = False):
        stmt = select(Article)

        if not with_deleted:
            stmt = stmt.where(Article.deleted.is_(False))

        result = await self.db.scalars(stmt)
        return result.all()
