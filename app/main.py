from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse

from app.exceptions.base import AppException
from app.middlewares.auth import AuthMiddleware
from app.routes.auth import router as auth_router
from app.routes.category import router as category_router

middleware = [
    Middleware(AuthMiddleware)
]
app = FastAPI(title='Marketplace blog', middleware=middleware)

app.include_router(auth_router)
app.include_router(category_router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get('/')
async def root():
    return {"message": "hi!"}
