from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.dependencies import get_user_service
from app.schemas.user import UserChangePassword, UserCreate, UserLogin, UserNewPassword
from app.services.user_service import UserService

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register')
async def register(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):

    token = await user_service.register_user(data)
    return{"message": 'User registered', "activation_token": token}


@router.post("/activate")
async def activate_user(
    token: str,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.activate_user(token)
    return {"message": "User activated"}


@router.post("/login")
async def login_user(
    data: UserLogin,
    user_service: UserService = Depends(get_user_service),
):
    token = await user_service.login_user(data)
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie("access_token", token, httponly=True)
    return response


@router.post("/logout")
async def logout_user(
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    token = request.cookies.get("access_token")
    if token:
        await user_service.logout_user(token)

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    return response

@router.post("/request-reset")
async def request_password_reset(
    data: UserChangePassword,
    user_service: UserService = Depends(get_user_service),
):
    token = await user_service.request_password_reset(data.email)
    return {"message": "Password reset email sent", "reset_token": token}

@router.post("/reset-password")
async def reset_password(
    data: UserNewPassword,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.reset_password(data)
    return {"message": "Password reset successful"}
