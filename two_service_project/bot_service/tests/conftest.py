"""
Общие фикстуры для всех тестов Bot Service.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fakeredis.aioredis import FakeRedis
from aiogram.types import Message, User, Chat


@pytest.fixture
def fake_redis():
    """Фикстура для фейкового Redis (in-memory)."""
    redis = FakeRedis(decode_responses=True)
    yield redis
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


@pytest.fixture(autouse=True)
def mock_redis_dependency(fake_redis):
    """Автоматически подменяет get_redis на фейковый Redis."""
    with patch('app.bot.handlers.get_redis', return_value=fake_redis):
        yield
        