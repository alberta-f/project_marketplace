from app.exceptions.base import AppException


class ArticleNotFoundException(AppException):
    status_code = 404
    detail = "Article not found"
