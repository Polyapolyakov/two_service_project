from typing import Annotated, AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_user_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(session)

async def get_auth_usecase(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)]
) -> AuthUseCase:
    return AuthUseCase(user_repo)

async def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> int:
    try:
        payload = security.decode_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise InvalidTokenError()
        return int(user_id_str)
    except ValueError as e:
        # Здесь нужно различать тип ошибки
        error_msg = str(e)
        if "истек" in error_msg.lower():
            raise TokenExpiredError() from e
        raise InvalidTokenError() from e
