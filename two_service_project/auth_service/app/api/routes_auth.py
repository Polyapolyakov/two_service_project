from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError
)
from app.schemas import auth as auth_schemas, user as user_schemas
from app.api import deps
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=user_schemas.UserPublic)
async def register(
    user_data: auth_schemas.RegisterRequest,
    auth_usecase: Annotated[AuthUseCase, Depends(deps.get_auth_usecase)]
):
    """
    Регистрация нового пользователя.
    Требования к email:
    - Должен быть в формате surname@email.com
    - Пример: ivanov@email.com
    """
    try:
        user = await auth_usecase.register(user_data.email, user_data.password)
        return user
    except UserAlreadyExistsError as e:
        raise e
    
@router.post("/login", response_model=auth_schemas.TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_usecase: Annotated[AuthUseCase, Depends(deps.get_auth_usecase)]
):
    """
    OAuth2 совместимый логин.
    Для входа используйте:
    - **username**: ваш email (в формате surname@email.com)
    - **password**: ваш пароль
    """
    try:
        token = await auth_usecase.login(form_data.username, form_data.password)
        return auth_schemas.TokenResponse(access_token=token)
    except InvalidCredentialsError as e:
        raise e

@router.get("/me", response_model=user_schemas.UserPublic)
async def get_my_profile(
    user_id: Annotated[int, Depends(deps.get_current_user_id)],
    auth_usecase: Annotated[AuthUseCase, Depends(deps.get_auth_usecase)]
):
    try:
        return await auth_usecase.get_profile(user_id)
    except UserNotFoundError as e:
        raise e
