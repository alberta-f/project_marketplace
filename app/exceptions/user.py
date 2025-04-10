from app.exceptions.base import AppException


class UserAlreadyExistsException(AppException):
    status_code = 400
    detail = "User already exists"

class InvalidCredentialsException(AppException):
    status_code = 401
    detail = "Invalid email or password"

class NotAuthenticatedException(AppException):
    status_code = 401
    detail = "Not authenticated"
