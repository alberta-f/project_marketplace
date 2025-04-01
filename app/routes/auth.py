from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import config
from app.db.session import get_db_session
from app.models.models import User
from app.schemas.user import UserChangePassword, UserCreate, UserLogin, UserNewPassword, UserRead
from app.services.auth import hash_paasword, verify_password
from app.services.jwt import (
    create_token,
    decode_token,
    delete_all_user_access_tokens,
    delete_token,
    verify_token,
)
from app.services.redis import get_redis_key
from app.tasks.email import send_email_task

auth_router = APIRouter()


@auth_router.post('/register') #, response_model=UserRead)
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

    token = await create_token(user_id=user.id,
                         token_type='email')

    confirm_link = f"{config.app.url}/auth/confirm-email?token={token}"
    send_email_task.delay(user.email, 'Регистрация', f'Подтверди по ссылке {confirm_link}')

    return {"user": user, "confirm_link": confirm_link}


@auth_router.get('/confirm_email')
async def confirm_email(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
):

    user_id = await verify_token(token=token,
                                 exc_token_type='email')

    if not user_id:
        raise HTTPException(status_code=400,
                            detail='Invalid or expired token')

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404,
                            detail='User not found')

    user.is_active = True
    await db.commit()

    return {"detail": "Email confirmed successfully ✅"}


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

    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Email not confirmed")

    token = await create_token(user.id, token_type='access')

    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        max_age=config.jwt.access_expire_mins * 60,
        samesite='lax',
        secure=False #!!!!! поменять на True
    )

    return user


@auth_router.get('/me', response_model=UserRead)
async def get_me(request: Request):
    user = request.state.user

    if not user:
        raise HTTPException(status_code=401,
                            detail='Unauthoriszed')

    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Email not confirmed")

    return user


@auth_router.post('/logout')
async def logout(request: Request, response: Response):
    token = request.cookies.get("access_token")

    if token:
        payload = await decode_token(token)
        user_id = payload.get("sub") if payload else None

        if user_id:
            redis_key = await get_redis_key(token=token,
                                  user_id=user_id,
                                  token_type='access')

            await delete_token(redis_key)

    response = JSONResponse(content={"detail": "Logged out"})
    response.delete_cookie("access_token")

    return response


@auth_router.post('/password_reset')
async def password_reset(
    data: UserChangePassword,
    db: AsyncSession = Depends(get_db_session)
):

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404,
                            detail='User not found')

    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Email not confirmed")

    token = await create_token(user_id=user.id,
                               token_type='password')

    reset_link = f"{config.app.url}/auth/redirect?token={token}"
    send_email_task.delay(user.email, 'Смена пароля', f'Подтверди смену пароля {reset_link}')

    return {"reset_link": reset_link}


@auth_router.get('/redirect')
async def get_token_for_new_password(token: str = Query(...)):
    return {"token": token}


@auth_router.post('/new_password')
async def new_password(
    data: UserNewPassword,
    db: AsyncSession = Depends(get_db_session)
):

    user_id = await verify_token(token=data.token,
                                 exc_token_type='password')

    if not user_id:
        raise HTTPException(status_code=400,
                            detail="Invalid or expired token")

    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404,
                            detail='User not found')

    user.hashed_password = hash_paasword(data.new_password)

    await delete_all_user_access_tokens(user_id)

    await db.commit()
    return {"detail": "Password changed successfully ✅"}


@auth_router.delete('/delete_user')
async def delete_user(request: Request,
                      db: AsyncSession = Depends(get_db_session)
):
    user = request.state.user

    if not user:
        raise HTTPException(status_code=401,
                            detail='Unauthoriszed')

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Email not confirmed")

    db_user = await db.get(User, user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()

    await delete_all_user_access_tokens(user.id)

    return {"detail": "User deleted successfully"}
