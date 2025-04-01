from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import config
from app.db.session import get_db_session
from app.models.models import User
from app.routes.auth import auth_router
from app.schemas.user import UserCreate
from app.services.auth import hash_paasword
from app.services.jwt import create_token, verify_token
from app.tasks.email import send_email_task


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
