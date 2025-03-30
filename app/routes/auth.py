from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import config
from app.db.session import get_db_session
from app.models.models import User
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.auth import hash_paasword, verify_password
from app.services.jwt import create_access_token, store_token

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


@auth_router.post('/login', response_model=UserRead)
async def login(
    data: UserLogin,
    response: Response,
    session: AsyncSession = Depends(get_db_session)
):

    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = create_access_token(user.id)
    await store_token(user.id, token)

    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        max_age=config.jwt.access_expire_mins * 60,
        samesite='lax',
        secure=False #!!!!! поменять на True
    )

    return user
