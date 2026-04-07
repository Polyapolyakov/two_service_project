"""
Модульные тесты для функций безопасности.
Тестирует хеширование паролей и JWT без БД и HTTP.
"""
import pytest
from datetime import datetime, timezone
from jose import jwt

from app.core import security
from app.core.config import settings


class TestPasswordHashing:
    """Тесты хеширования паролей."""
    
    def test_hash_not_equal_to_password(self):
        """Хеш не должен быть равен исходному паролю."""
        password = "my_secret_password"
        hashed = security.get_password_hash(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_correct_password(self):
        """Проверка правильного пароля должна проходить."""
        password = "my_secret_password"
        hashed = security.get_password_hash(password)
        
        assert security.verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Проверка неправильного пароля должна не проходить."""
        password = "my_secret_password"
        wrong_password = "wrong_password"
        hashed = security.get_password_hash(password)
        
        assert security.verify_password(wrong_password, hashed) is False
    
    def test_verify_empty_password(self):
        """Проверка пустого пароля."""
        password = "password"
        hashed = security.get_password_hash(password)
        
        assert security.verify_password("", hashed) is False
    
    def test_different_passwords_produce_different_hashes(self):
        """Разные пароли дают разные хеши."""
        hash1 = security.get_password_hash("password1")
        hash2 = security.get_password_hash("password2")
        
        assert hash1 != hash2


class TestJWT:
    """Тесты JWT токенов."""
    
    def test_create_access_token_contains_required_fields(self):
        """Токен должен содержать sub, role, iat, exp."""
        payload = {"sub": "123", "role": "user"}
        token = security.create_access_token(payload)
        
        # Декодируем токен
        decoded = security.decode_token(token)
        
        # Проверяем наличие всех полей
        assert "sub" in decoded
        assert "role" in decoded
        assert "iat" in decoded
        assert "exp" in decoded
        
        # Проверяем значения
        assert decoded["sub"] == "123"
        assert decoded["role"] == "user"
    
    def test_create_access_token_with_custom_expiry(self):
        """Тест создания токена с кастомным временем жизни."""
        from datetime import timedelta
        
        payload = {"sub": "1", "role": "user"}
        expires_delta = timedelta(minutes=30)
        token = security.create_access_token(payload, expires_delta)
        
        decoded = security.decode_token(token)
        
        # Проверяем, что время жизни примерно 30 минут
        exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(decoded["iat"], tz=timezone.utc)
        diff = (exp - iat).total_seconds() / 60
        
        assert 29 <= diff <= 31  # Примерно 30 минут
    
    def test_decode_valid_token(self):
        """Декодирование валидного токена должно возвращать payload."""
        payload = {"sub": "42", "role": "admin"}
        token = security.create_access_token(payload)
        
        decoded = security.decode_token(token)
        
        assert decoded["sub"] == "42"
        assert decoded["role"] == "admin"
    
    def test_decode_invalid_token_raises_error(self):
        """Декодирование невалидного токена должно вызывать ошибку."""
        invalid_token = "this.is.not.a.valid.token"
        
        with pytest.raises(ValueError, match="Не удалось проверить токен"):
            security.decode_token(invalid_token)
    
    def test_decode_expired_token_raises_error(self):
        """Декодирование просроченного токена должно вызывать ошибку."""
        from datetime import timedelta
        
        payload = {"sub": "1", "role": "user"}
        # Создаем токен с отрицательным временем жизни
        expires_delta = timedelta(seconds=-1)
        token = security.create_access_token(payload, expires_delta)
        
        with pytest.raises(ValueError, match="Не удалось проверить токен"):
            security.decode_token(token)
    
    def test_token_has_correct_algorithm(self):
        """Проверка, что токен использует правильный алгоритм."""
        payload = {"sub": "1", "role": "user"}
        token = security.create_access_token(payload)
        
        # Проверяем заголовок токена
        header = jwt.get_unverified_header(token)
        assert header["alg"] == settings.JWT_ALG
