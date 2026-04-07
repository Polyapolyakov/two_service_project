"""
Мок-тесты для обработчиков Telegram.
Используют fakeredis и моки Celery, не требуют реальных сервисов.
"""
import pytest
from unittest.mock import AsyncMock, patch
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.bot.handlers import cmd_start, cmd_token, handle_message


class TestStartHandler:
    """Тесты обработчика команды /start."""
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_message):
        """Тест команды /start."""
        mock_message.text = "/start"
        
        await cmd_start(mock_message)
        
        mock_message.answer.assert_called_once()
        answer_text = mock_message.answer.call_args[0][0]
        assert "Привет" in answer_text
        assert "/token" in answer_text


class TestTokenHandler:
    """Тесты обработчика команды /token."""
    
    @pytest.mark.asyncio
    async def test_token_command_without_token(self, mock_message):
        """Тест команды /token без токена."""
        mock_message.text = "/token"
        
        await cmd_token(mock_message)
        
        mock_message.answer.assert_called_once()
        assert "Пожалуйста, укажите токен" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_token_command_with_valid_token(self, mock_message, fake_redis):
        """Тест команды /token с валидным токеном."""
        # Создаем валидный токен
        payload = {"sub": "123", "role": "user"}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        mock_message.text = f"/token {token}"
        
        await cmd_token(mock_message)
        
        # Проверяем, что токен сохранился в Redis
        key = f"tg_token:{mock_message.from_user.id}"
        saved_token = await fake_redis.get(key)
        assert saved_token == token
        
        # Проверяем ответ бота
        mock_message.answer.assert_called_once()
        assert "успешно сохранен" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_token_command_with_invalid_token(self, mock_message, fake_redis):
        """Тест команды /token с невалидным токеном."""
        invalid_token = "invalid.token.here"
        mock_message.text = f"/token {invalid_token}"
        
        await cmd_token(mock_message)
        
        # Проверяем, что токен НЕ сохранился в Redis
        key = f"tg_token:{mock_message.from_user.id}"
        saved_token = await fake_redis.get(key)
        assert saved_token is None
        
        # Проверяем сообщение об ошибке
        mock_message.answer.assert_called_once()
        assert "Ошибка валидации токена" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_token_command_with_expired_token(self, mock_message, fake_redis):
        """Тест команды /token с просроченным токеном."""
        # Создаем просроченный токен
        payload = {
            "sub": "123",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        mock_message.text = f"/token {token}"
        
        await cmd_token(mock_message)
        
        # Проверяем, что токен НЕ сохранился
        key = f"tg_token:{mock_message.from_user.id}"
        saved_token = await fake_redis.get(key)
        assert saved_token is None
        
        mock_message.answer.assert_called_once()
        assert "Токен истек" in mock_message.answer.call_args[0][0]


class TestMessageHandler:
    """Тесты обработчика обычных текстовых сообщений."""
    
    @pytest.mark.asyncio
    async def test_message_without_token(self, mock_message, fake_redis):
        """Тест: если токена нет, бот просит авторизоваться."""
        mock_message.text = "Привет!"
        
        await handle_message(mock_message)
        
        mock_message.answer.assert_called_once()
        answer_text = mock_message.answer.call_args[0][0]
        assert "нет сохраненного токена" in answer_text
    
    @pytest.mark.asyncio
    async def test_message_with_valid_token_sends_celery_task(
        self, mock_message, fake_redis, mock_celery_task
    ):
        """Тест: с валидным токеном бот отправляет задачу в Celery."""
        # Сохраняем валидный токен в Redis
        payload = {"sub": "123", "role": "user"}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        key = f"tg_token:{mock_message.from_user.id}"
        await fake_redis.set(key, token)
        
        mock_message.text = "Как дела?"
        
        await handle_message(mock_message)
        
        # Проверяем, что Celery задача была вызвана
        mock_celery_task.assert_called_once_with("Как дела?", 0.7)
        
        # Проверяем ответ бота
        mock_message.answer.assert_called_once()
        assert "Обрабатываю" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_message_with_invalid_token(
        self, mock_message, fake_redis, mock_celery_task
    ):
        """Тест: с невалидным токеном бот не вызывает Celery."""
        # Сохраняем невалидный токен в Redis
        invalid_token = "invalid.token.here"
        key = f"tg_token:{mock_message.from_user.id}"
        await fake_redis.set(key, invalid_token)
        
        mock_message.text = "Привет!"
        
        await handle_message(mock_message)
        
        # Проверяем, что Celery задача НЕ была вызвана
        mock_celery_task.assert_not_called()
        
        mock_message.answer.assert_called_once()
        assert "недействителен" in mock_message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_message_with_expired_token(
        self, mock_message, fake_redis, mock_celery_task
    ):
        """Тест: с просроченным токеном бот не вызывает Celery."""
        # Создаем просроченный токен
        payload = {"sub": "123", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}
        expired_token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        key = f"tg_token:{mock_message.from_user.id}"
        await fake_redis.set(key, expired_token)
        
        mock_message.text = "Привет!"
        
        await handle_message(mock_message)
        
        mock_celery_task.assert_not_called()
        mock_message.answer.assert_called_once()
        assert "недействителен" in mock_message.answer.call_args[0][0]
