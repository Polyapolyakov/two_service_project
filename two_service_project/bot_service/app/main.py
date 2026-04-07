"""
Главный файл приложения Bot Service.
Запускает только Telegram бота (без FastAPI).
"""
import asyncio
from app.bot.dispatcher import bot, dp


async def main():
    """Запуск Telegram бота."""
    print("🚀 Запуск Telegram бота...")
    print("✅ Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    