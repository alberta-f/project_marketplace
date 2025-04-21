from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse

from app.dependencies import get_token_service, get_user_service
from app.routes.utils.cookie import get_user_from_cookie, set_token_to_cookie
from app.schemas.user import UserCreate, UserLogin, UserRead, UserUpdate
from app.services.token import TokenService
from app.services.user import UserService

router = APIRouter(prefix='/users', tags=['Users'])


@router.post("/register", response_model=UserRead)
async def register(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.register_user(data)
    return user


@router.post("/login")
async def login(
    response: Response,
    data: UserLogin,
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service)
):
    user = await user_service.login_user(data)

    token = token_service.create_access_token(user.id)
    set_token_to_cookie(response, token)

    return {"message": "Login successful", "user_id": user.id}


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

@router.get('/me', response_model=UserRead)
async def get_me(request: Request,
                 response: Response,
                 token_service: TokenService = Depends(get_token_service)):
    user = get_user_from_cookie(request)

    token = token_service.create_access_token(user.id)
    set_token_to_cookie(response, token)

    return user


@router.put('/me')
async def put_me(request: Request,
                 data: UserUpdate,
                 user_service: UserService = Depends(get_user_service),
                 ):
    user = get_user_from_cookie(request)

    await user_service.update_user(user, data)
    return Response(status_code=204, content='User updated successfully')


@router.delete('/me')
async def delete_user(request: Request,
                      user_service: UserService = Depends(get_user_service)
):
    user = get_user_from_cookie(request)

    await user_service.delete_user(user)
    return Response(status_code=204, content="User deleted successfully")


@router.get('/all', response_model=list[UserRead])
async def get_all_users(user_service: UserService=Depends(get_user_service)):
    return await user_service.get_all()
