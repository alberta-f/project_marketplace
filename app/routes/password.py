from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import config
from app.db.session import get_db_session
from app.models.models import User
from app.routes.auth import auth_router
from app.schemas.user import UserChangePassword, UserNewPassword
from app.services.auth import hash_paasword
from app.services.jwt import create_token, delete_all_user_access_tokens, verify_token
from app.tasks.email import send_email_task


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
