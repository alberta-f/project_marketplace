from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db_session
from app.models.models import User
from app.schemas.user import UserCreate, UserRead
from app.services.auth import hash_paasword

auth_router = APIRouter()


@auth_router.post('/register', response_model=UserRead)
async def register(data: UserCreate,
                   db_session: AsyncSession = Depends(get_db_session)):

    query = select(User).where(User.email == data.email)
    result = await db_session.execute(query)

    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400,
                            detail='Email already registered')

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_paasword(data.password)
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user
