from app.exceptions.base import AppException


class CategoryAlreadyExistsException(AppException):
    status_code = 400
    detail = "Category already exists"


class CategoryNotFoundException(AppException):
    status_code = 404
    detail = "Category not found"
