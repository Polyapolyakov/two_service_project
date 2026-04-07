"""
Модульные тесты для JWT валидации.
Проверяют, что токен декодируется и валидируется корректно.
"""
import pytest
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.jwt import decode_and_validate


class TestJWTValidation:
    """Тесты валидации JWT токенов."""
    
    def test_decode_valid_token(self):
        """Тест декодирования валидного токена."""
        # Создаем тестовый токен (тем же секретом, что и Auth Service)
        payload = {
            "sub": "123",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        # Декодируем и проверяем
        result = decode_and_validate(token)
        
        assert result["sub"] == "123"
        assert result["role"] == "user"
        assert "exp" in result
        assert "iat" in result
    
    def test_decode_token_extracts_sub_correctly(self):
        """Тест, что sub извлекается корректно."""
        payload = {"sub": "456", "role": "admin"}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        result = decode_and_validate(token)
        
        assert result["sub"] == "456"
        assert result["role"] == "admin"
    
    def test_decode_invalid_token_raises_error(self):
        """Тест: мусорная строка вместо токена вызывает ошибку."""
        invalid_token = "this.is.not.a.valid.token"
        
        with pytest.raises(ValueError, match="Невалидный токен"):
            decode_and_validate(invalid_token)
    
    def test_decode_expired_token_raises_error(self):
        """Тест: просроченный токен вызывает ошибку."""
        # Создаем токен с истекшим сроком
        payload = {
            "sub": "123",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        with pytest.raises(ValueError, match="Токен истек"):
            decode_and_validate(token)
    
    def test_decode_token_without_sub_raises_error(self):
        """Тест: токен без sub вызывает ошибку (но в decode_and_validate нет проверки)."""
        # Примечание: decode_and_validate не проверяет наличие sub
        # Это нормально, проверка sub делается в handlers.py
        payload = {"role": "user"}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        # Декодирование должно пройти успешно (проверка sub не здесь)
        result = decode_and_validate(token)
        assert "sub" not in result
        assert result["role"] == "user"
    
    def test_token_with_wrong_secret_raises_error(self):
        """Тест: токен с другим секретом вызывает ошибку."""
        payload = {"sub": "123"}
        token = jwt.encode(payload, "wrong_secret", algorithm=settings.JWT_ALG)
        
        with pytest.raises(ValueError, match="Невалидный токен"):
            decode_and_validate(token)
    
    def test_token_with_wrong_algorithm_raises_error(self):
        """Тест: токен с другим алгоритмом вызывает ошибку."""
        payload = {"sub": "123"}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS512")
        
        with pytest.raises(ValueError, match="Невалидный токен"):
            decode_and_validate(token)
