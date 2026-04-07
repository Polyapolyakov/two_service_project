"""
Общие фикстуры для всех тестов Bot Service.
Здесь настраивается мокирование Redis и других зависимостей.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fakeredis.aioredis import FakeRedis
from aiogram.types import Message, User, Chat

# Глобальная настройка для fakeredis
@pytest.fixture
def fake_redis():
    """Фикстура для фейкового Redis (in-memory)."""
    redis = FakeRedis(decode_responses=True)
    yield redis
    # Очистка после тестов
    redis.flushall()
    redis.close()


@pytest.fixture
def mock_message():
    """Фикстура для мока сообщения Telegram."""
    message = AsyncMock(spec=Message)
    message.from_user = User(id=12345, is_bot=False, first_name="Test")
    message.chat = Chat(id=12345, type="private")
    message.text = ""
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_celery_task():
    """Фикстура для мока Celery задачи."""
    with patch('app.tasks.llm_tasks.llm_request.delay') as mock_delay:
        mock_delay.return_value = AsyncMock(id="test-task-id")
        yield mock_delay


# Автоматическое мокирование get_redis для всех тестов
@pytest.fixture(autouse=True)
def mock_redis_dependency(fake_redis):
    """
    Автоматически подменяет get_redis на фейковый Redis для всех тестов.
    """
    with patch('app.bot.handlers.get_redis', return_value=fake_redis):
        yield
