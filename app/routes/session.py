from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import config
from app.db.session import get_db_session
from app.models.models import User
from app.routes.auth import auth_router
from app.schemas.user import UserLogin, UserRead
from app.services.auth import verify_password
from app.services.deps import get_current_user
from app.services.jwt import create_token, decode_token, delete_all_user_access_tokens, delete_token
from app.services.redis import get_redis_key


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
async def get_me(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401,
                            detail='Unauthoriszed')

    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Email not confirmed")

    return user


@auth_router.post('/logout')
async def logout(request: Request,
                 response: Response):

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


@auth_router.post('/logout_from_all_sessions')
async def logout_from_all_sessions(user: User = Depends(get_current_user)):
    await delete_all_user_access_tokens(user.id)
    return {"detail": "Logged out from all sessions ✅"}


@auth_router.delete('/delete_user')
async def delete_user(user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db_session)
):
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
