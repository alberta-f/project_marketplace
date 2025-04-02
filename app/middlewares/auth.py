from sqlalchemy.future import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.models.models import User
from app.services.db import async_session_maker
from app.services.jwt import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> Response:
        request.state.user = None
        token = request.cookies.get('access_token')

        if token:
            user_id = await verify_token(token=token,
                                         exc_token_type='access')

            if user_id:
                async with async_session_maker() as session:
                    res = await session.execute(select(User).where(User.id == user_id))
                    user = res.scalar_one_or_none()

                    if user:
                        request.state.user = user

        response = await call_next(request)
        return response
