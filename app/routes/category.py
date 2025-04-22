from fastapi import APIRouter, Depends, Request, Response

from app.dependencies import get_category_service
from app.routes.utils.cookie import get_user_from_cookie
from app.schemas.category import CategoryCreate, CategoryRead
from app.services.category import CategoryService

router = APIRouter(prefix='/category', tags=['Category'])


@router.post('/new', response_model=CategoryRead)
async def create_category(
    request: Request,
    data: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
):
    get_user_from_cookie(request)

    category = await category_service.create(data)
    return category


@router.get('/all', response_model=list[CategoryRead])
async def list_categories(
    category_service: CategoryService = Depends(get_category_service),
):
    return await category_service.list()


@router.get('/{category_id}')
async def get_category(
    category_id,
    category_service: CategoryService = Depends(get_category_service),
):
    return await category_service.get(category_id)

@router.delete("/delete/{category_id}", status_code=204)
async def delete_category(
    request: Request,
    category_id,
    category_service: CategoryService = Depends(get_category_service),
):
    get_user_from_cookie(request)

    await category_service.delete(category_id)
    return Response(status_code=204, content="User deleted successfully")
