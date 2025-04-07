from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repo.user import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserNewPassword, UserUpdate
from app.services.mail import MailService
from app.services.security import SecurityService
from app.services.token import TokenService


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        token_service: TokenService,
        security_service: SecurityService,
        mail_service: MailService,
    ):
        self.user_repo = UserRepository(db)
        self.token_service = token_service
        self.security = security_service
        self.mail_service = mail_service

    async def register_user(self, data: UserCreate) -> str:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = self.security.hash_password(data.password)
        user = User(email=data.email,
                    username=data.username,
                    hashed_password=hashed_password,
                    is_active=data.is_active)
        user = await self.user_repo.create(user)

        activation_token = await self.token_service.generate("activation", user.id)
        self.mail_service.send_activation_email(user.email, activation_token)

        return activation_token

    async def activate_user(self, token: str) -> None:
        user_id = await self.token_service.validate("activation", token)
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = True
        await self.user_repo.update(user)

    async def login_user(self, data: UserLogin) -> str:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not self.security.verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account not activated")

        return await self.token_service.generate("access", user.id)

    async def logout_user(self, token: str) -> None:
        payload = await self.token_service.repos["access"].decode_token(token)
        if not payload:
            raise HTTPException(status_code=403, detail='Not authenticated')

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=403, detail='Not authenticated')

        await self.token_service.delete("access", token, UUID(user_id))

    async def request_password_reset(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        reset_token = await self.token_service.generate("reset", user.id)
        self.mail_service.send_reset_email(user.email, reset_token)

        return reset_token

    async def reset_password(self, data: UserNewPassword) -> None:
        user_id = await self.token_service.validate("reset", data.token)
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.hashed_password = self.security.hash_password(data.new_password)
        await self.user_repo.update(user)

        await self.token_service.delete_all("access", user.id)


    async def put_user(self,
                       user: User,
                       data: UserUpdate):

        user.email = data.email
        user.username = data.username
        user.hashed_password = self.security.hash_password(data.password)

        await self.user_repo.update(user)


    async def delete_user(self, user: User):
        if not user:
            raise HTTPException(status_code=403, detail='Not authenticated')

        await self.user_repo.delete(user)
        await self.token_service.delete_all('access', user.id)


    async def get_user_from_cookie(self, request: Request):
        user = request.state.user

        if not user:
            raise HTTPException(status_code=401, detail='Not authenticated')

        if not user or not user.is_active:
            raise HTTPException(status_code=403, detail="Email not confirmed")

        return user
