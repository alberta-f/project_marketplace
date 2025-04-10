from app.exceptions.base import AppException


class ArticleNotFoundException(AppException):
    status_code = 404
    detail = "Article not found"


class DuplicateArticleTitleException(AppException):
    status_code = 400
    detail = "Article with this title already exists"
