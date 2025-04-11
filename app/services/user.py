from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from app.models.user import User
from app.repository.user import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from app.services.mail import MailService
from app.services.security import SecurityService


class UserService:
    def __init__(self, db: AsyncSession, security: SecurityService, mail: MailService):
        self.user_repository = UserRepository(db)
        self.security = security
        self.mail = mail


    async def register_user(self, data: UserCreate):
        existing = await self.user_repository.get_by_email(data.email)
        if existing:
            raise UserAlreadyExistsException()

        hashed_password = self.security.hash_password(data.password)
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hashed_password,
        )

        self.mail.send_registration_email(email=user.email)
        return await self.user_repository.create(user)


    async def login_user(self, data: UserLogin) -> User:
        user = await self.user_repository.get_by_email(data.email)
        if not user or not self.security.verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()
        return user


    async def update_user(self, user: User, data: UserUpdate) -> User:
        if not self.security.verify_password(data.old_password, user.hashed_password):
            raise InvalidCredentialsException()

        user.email = data.email
        user.username = data.username
        user.hashed_password = self.security.hash_password(data.new_password)

        return await self.user_repository.update(user)


    async def delete_user(self, user: User):
        return await self.user_repository.delete(user)
