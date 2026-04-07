"""
Интеграционные тесты для клиента OpenRouter.
Используют respx для мокирования HTTP-запросов без реального интернета.
"""
import pytest
import respx
from httpx import Response

from app.services.openrouter_client import OpenRouterClient
from app.core.config import settings


class TestOpenRouterClient:
    """Тесты клиента OpenRouter."""
    
    @pytest.mark.asyncio
    async def test_ask_successful_response(self):
        """Тест успешного ответа от OpenRouter."""
        # Настраиваем мок роут
        expected_answer = "Привет! Это тестовый ответ от LLM."
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": expected_answer
                    }
                }
            ]
        }
        
        # Поднимаем мок-роут
        with respx.mock(
            base_url=settings.OPENROUTER_BASE_URL,
            assert_all_called=False
        ) as respx_mock:
            respx_mock.post("/chat/completions").mock(
                return_value=Response(200, json=mock_response)
            )
            
            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Привет!"}]
            
            result = await client.ask(messages, temperature=0.7)
            
            assert result == expected_answer
            # Проверяем, что запрос был сделан
            assert respx_mock["/chat/completions"].called
    
    @pytest.mark.asyncio
    async def test_ask_handles_http_error(self):
        """Тест обработки HTTP ошибки."""
        with respx.mock(base_url=settings.OPENROUTER_BASE_URL) as respx_mock:
            respx_mock.post("/chat/completions").mock(
                return_value=Response(401, json={"error": "Unauthorized"})
            )
            
            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Привет!"}]
            
            with pytest.raises(Exception) as exc_info:
                await client.ask(messages, temperature=0.7)
            
            assert "401" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_ask_handles_network_error(self):
        """Тест обработки сетевой ошибки."""
        with respx.mock(base_url=settings.OPENROUTER_BASE_URL) as respx_mock:
            respx_mock.post("/chat/completions").mock(side_effect=Exception("Network error"))
            
            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Привет!"}]
            
            with pytest.raises(Exception) as exc_info:
                await client.ask(messages, temperature=0.7)
            
            assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_ask_constructs_correct_payload(self):
        """Тест формирования правильного payload."""
        with respx.mock(base_url=settings.OPENROUTER_BASE_URL) as respx_mock:
            respx_mock.post("/chat/completions").mock(
                return_value=Response(200, json={"choices": [{"message": {"content": "OK"}}]})
            )
            
            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Test"}]
            
            await client.ask(messages, temperature=0.5)
            
            # Проверяем, что запрос содержал правильные данные
            request = respx_mock.calls.last.request
            import json
            body = json.loads(request.content)
            
            assert body["model"] == settings.OPENROUTER_MODEL
            assert body["messages"] == messages
            assert body["temperature"] == 0.5
    
    @pytest.mark.asyncio
    async def test_ask_sets_correct_headers(self):
        """Тест установки правильных заголовков."""
        with respx.mock(base_url=settings.OPENROUTER_BASE_URL) as respx_mock:
            respx_mock.post("/chat/completions").mock(
                return_value=Response(200, json={"choices": [{"message": {"content": "OK"}}]})
            )
            
            client = OpenRouterClient()
            messages = [{"role": "user", "content": "Test"}]
            
            await client.ask(messages, temperature=0.7)
            
            # Проверяем заголовки
            request = respx_mock.calls.last.request
            headers = request.headers
            
            assert headers["Authorization"] == f"Bearer {settings.OPENROUTER_API_KEY}"
            assert headers["Content-Type"] == "application/json"
            assert headers["HTTP-Referer"] == settings.OPENROUTER_SITE_URL
            assert headers["X-Title"] == settings.OPENROUTER_APP_NAME
