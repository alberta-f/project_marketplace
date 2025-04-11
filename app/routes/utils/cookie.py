from fastapi import Request, Response

from app.core.config import config
from app.exceptions.user import NotAuthenticatedException


def set_token_to_cookie(response: Response, token):
    response.set_cookie(
        key=config.session.cookie_name,
        value=token,
        httponly=True,
        secure=False,  # True на проде
        samesite="lax",
    )


def get_user_from_cookie(request: Request):
    user = request.state.user
    if not user:
        raise NotAuthenticatedException()

    return user
