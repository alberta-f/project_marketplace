from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repo.db_base import DBRepository


class UserRepository(DBRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)


    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
