"""
Интеграционные тесты API Auth Service.
Тестирует полный пользовательский сценарий через HTTP.
"""
import pytest
from httpx import AsyncClient


class TestAuthAPI:
    """Тесты эндпоинтов аутентификации."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Успешная регистрация пользователя."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "ivanov@email.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "ivanov@email.com"
        assert "id" in data
        assert "role" in data
        assert "created_at" in data
        assert data["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_register_invalid_email_format(self, client: AsyncClient):
        """Регистрация с невалидным email."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "ivanov@gmail.com",  # неверный домен
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
        error_detail = str(response.json())
        assert "email" in error_detail.lower()
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Регистрация с уже существующим email."""
        # Первая регистрация
        await client.post(
            "/auth/register",
            json={"email": "duplicate@email.com", "password": "pass123"}
        )
        
        # Вторая регистрация с тем же email
        response = await client.post(
            "/auth/register",
            json={"email": "duplicate@email.com", "password": "pass123"}
        )
        
        assert response.status_code == 409  # Conflict
        assert "уже существует" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Регистрация с коротким паролем."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "ivanov@email.com",
                "password": "123"  # меньше 6 символов
            }
        )
        
        assert response.status_code == 422
        assert "ensure this value has at least 6 characters" in str(response.json())
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Успешный логин."""
        # Сначала регистрируемся
        await client.post(
            "/auth/register",
            json={"email": "login@email.com", "password": "password123"}
        )
        
        # Затем логинимся
        response = await client.post(
            "/auth/login",
            data={
                "username": "login@email.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Логин с неверным паролем."""
        # Регистрируемся
        await client.post(
            "/auth/register",
            json={"email": "wrongpass@email.com", "password": "correct123"}
        )
        
        # Логинимся с неверным паролем
        response = await client.post(
            "/auth/login",
            data={
                "username": "wrongpass@email.com",
                "password": "wrong123"
            }
        )
        
        assert response.status_code == 401
        assert "Неверный" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Логин с несуществующим пользователем."""
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistent@email.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "Неверный" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_me_with_valid_token(self, client: AsyncClient):
        """Получение профиля с валидным токеном."""
        # Регистрируемся
        await client.post(
            "/auth/register",
            json={"email": "me@email.com", "password": "password123"}
        )
        
        # Логинимся
        login_response = await client.post(
            "/auth/login",
            data={
                "username": "me@email.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Запрашиваем профиль
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@email.com"
        assert "id" in data
        assert "role" in data
        assert "created_at" in data
        assert "password_hash" not in data  # пароль не должен быть в ответе
    
    @pytest.mark.asyncio
    async def test_get_me_without_token(self, client: AsyncClient):
        """Получение профиля без токена."""
        response = await client.get("/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_me_with_invalid_token(self, client: AsyncClient):
        """Получение профиля с невалидным токеном."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
        assert "Недействительный" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_full_user_flow(self, client: AsyncClient):
        """Полный пользовательский сценарий."""
        email = "fullflow@email.com"
        password = "securepassword123"
        
        # 1. Регистрация
        register_response = await client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )
        assert register_response.status_code == 200
        user_id = register_response.json()["id"]
        
        # 2. Логин
        login_response = await client.post(
            "/auth/login",
            data={"username": email, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Получение профиля
        me_response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["id"] == user_id
        assert me_response.json()["email"] == email
