from app.repositories.users import UserRepository
from app.core import security
from app.core.exceptions import (
UserAlreadyExistsError,
InvalidCredentialsError,
UserNotFoundError
)
from app.schemas.user import UserPublic

class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, password: str) -> UserPublic:
        # Проверка существования пользователя
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()
        
        # Хеширование пароля (репозиторий не знает о паролях)
        hashed = security.get_password_hash(password)
        
        # Создание пользователя
        user = await self.user_repo.create(email, hashed)
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> str:
        # Поиск пользователя
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()
        
        # Проверка пароля (репозиторий не знает о паролях)
        if not security.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        
        # Создание токена (репозиторий не знает о JWT)
        token_data = {"sub": str(user.id), "role": user.role}
        return security.create_access_token(token_data)

    async def get_profile(self, user_id: int) -> UserPublic:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return UserPublic.model_validate(user)
