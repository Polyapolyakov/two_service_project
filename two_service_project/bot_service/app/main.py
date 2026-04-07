"""
Главный файл приложения Bot Service.
Запускает FastAPI сервер и Telegram бота в одном процессе.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bot.dispatcher import bot, dp
from app.core.config import settings
from app.infra.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    Запускает Telegram бота при старте и останавливает при завершении.
    """
    # Запуск: стартуем polling бота в фоновом режиме
    print("🚀 Запуск Telegram бота...")
    polling_task = asyncio.create_task(dp.start_polling(bot))
    print("✅ Бот запущен и готов к работе!")
    
    yield  # Здесь приложение работает
    
    # Остановка: отменяем polling и закрываем соединения
    print("🛑 Остановка Telegram бота...")
    polling_task.cancel()
    await close_redis()
    print("✅ Бот остановлен")


def create_app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check для проверки работоспособности
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "ok",
            "service": settings.APP_NAME,
            "environment": settings.ENV
        }
    
    return app


# Создаем экземпляр приложения
app = create_app()
  