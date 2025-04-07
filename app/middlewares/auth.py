from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.dependencies import get_user_service  # Для получения UserService через Depends
from app.services.user import UserService


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> Response:
        request.state.user = None

        token = request.cookies.get('access_token')

        if token:
            user_service: UserService = get_user_service()

            user_id = await user_service.token_service.validate("access", token)

            if user_id:
                user = await user_service.user_repo.get_by_id(user_id)

                if user:
                    request.state.user = user

        response = await call_next(request)
        return response
