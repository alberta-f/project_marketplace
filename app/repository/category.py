from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.repository.db_base import DBRepository


class CategoryRepository(DBRepository[Category]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Category)


    async def get_by_name(self, name: str):
        stmt = select(Category).where(Category.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    async def get_categories_by_ids(self, ids):
        result = await self.db.scalars(select(Category).where(Category.id.in_(ids)))
        return result.all()
