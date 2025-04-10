from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.category import CategoryAlreadyExistsException, CategoryNotFoundException
from app.models.category import Category
from app.repository.category import CategoryRepository
from app.schemas.category import CategoryCreate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.category_repository = CategoryRepository(db)

    async def create(self, data: CategoryCreate):
        existing = await self.category_repository.get_by_name(data.name)
        if existing:
            raise CategoryAlreadyExistsException()

        category = Category(name=data.name)
        return await self.category_repository.create(category)

    async def get(self, category_id):
        category = await self.category_repository.get_by_id(category_id)

        if not category:
            raise CategoryNotFoundException()

        return category

    async def list(self):
        return await self.category_repository.get_all()

    async def delete(self, category_id):
        category = await self.category_repository.get_by_id(category_id)
        await self.category_repository.delete(category)
