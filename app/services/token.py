from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import config
from app.exceptions.user import NotAuthenticatedException


class TokenService:
    @staticmethod
    def create_access_token(user_id: UUID) -> str:
        expire = datetime.now() + timedelta(minutes=config.jwt.single_use_expire_mins)
        payload = {
            "sub": str(user_id),
            "exp": expire,
        }
        return jwt.encode(
            payload,
            config.jwt.secret_key,
            algorithm=config.jwt.algorithm
        )

    @staticmethod
    def decode_access_token(token: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                config.jwt.secret_key,
                algorithms=[config.jwt.algorithm]
            )

            user_id = payload.get("sub")

            if not user_id:
                raise NotAuthenticatedException()

            return UUID(user_id)

        except JWTError:
            raise NotAuthenticatedException()


def get_token_service():
    return TokenService()
