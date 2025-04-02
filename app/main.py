from fastapi import FastAPI
from fastapi.middleware import Middleware

from app.middlewares.auth import AuthMiddleware
from app.routes.auth import router

middleware = [
    Middleware(AuthMiddleware)
]
app = FastAPI(title='Marketplace blog', middleware=middleware)

app.include_router(router)

@app.get('/')
async def root():
    return {"message": "hi!"}
