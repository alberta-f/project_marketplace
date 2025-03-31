from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_active: bool = False


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    is_active: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserChangePassword(BaseModel):
    email: EmailStr


class UserNewPassword(BaseModel):
    token: str
    new_password: str
