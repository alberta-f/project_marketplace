from fastapi import Request, Response

from app.core.config import config
from app.exceptions.user import NotAuthenticatedException


def set_token_to_cookie(response: Response, token):
    response.set_cookie(
        key=config.session.cookie_name,
        value=token,
        path="/",
        httponly=False,
        secure=True,
        samesite="lax",
    )


def get_user_from_cookie(request: Request):
    user = request.state.user
    if not user:
        raise NotAuthenticatedException()

    return user
