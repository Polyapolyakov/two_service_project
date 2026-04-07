import asyncio
from celery import shared_task
from aiogram import Bot

from app.core.config import settings
from app.services.openrouter_client import OpenRouterClient


@shared_task(name="llm_request", bind=True)
def llm_request(self, prompt: str, user_id: int, temperature: float = 0.7) -> str:
    
    client = OpenRouterClient()
    messages = [{"role": "user", "content": prompt}]
    
    async def _process():
        """Асинхронная обработка запроса."""
        bot = None
        try:
            # Получаем ответ от LLM
            answer = await client.ask(messages, temperature)
            
            # Отправляем ответ пользователю в Telegram
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=user_id,
                text=f"**Ответ:**\n\n{answer}",
                parse_mode="Markdown"
            )
            
            return answer
            
        except Exception as e:
            error_msg = f"Ошибка при обращении к LLM: {str(e)}"
            
            # Отправляем сообщение об ошибке пользователю
            try:
                if bot is None:
                    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                await bot.send_message(
                    chat_id=user_id,
                    text=f"**Ошибка:**\n\n{error_msg}\n\nПожалуйста, попробуйте позже.",
                    parse_mode="Markdown"
                )
            except Exception as send_error:
                # Логируем ошибку отправки, но не прерываем выполнение
                print(f"Не удалось отправить сообщение об ошибке: {send_error}")
            
            return error_msg
            
        finally:
            # Закрываем сессию бота, если она была создана
            if bot:
                await bot.session.close()
    
    # Запускаем асинхронную функцию в синхронном контексте Celery
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_process())
        return result
    finally:
        loop.close()
