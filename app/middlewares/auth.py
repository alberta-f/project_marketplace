from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import config
from app.core.database import get_db
from app.dependencies import get_token_service
from app.exceptions.user import NotAuthenticatedException
from app.repository.user import UserRepository


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next) -> Response:
        request.state.user = None
        token = request.cookies.get(config.session.cookie_name)

        try:
            token_service = get_token_service()
            user_id = token_service.decode_access_token(token)

            if user_id:
                async for session in get_db():
                    repo = UserRepository(session)
                    user = await repo.get_by_id(user_id)

                if user:
                    request.state.user = user

        except NotAuthenticatedException:
            request.state.user = None

        except Exception:
            pass

        response = await call_next(request)
        return response
