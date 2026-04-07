from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from app.core.config import settings
from app.bot.handlers import router

# Создаем бота с parse_mode=None (отключаем HTML парсинг)
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=None)  # ← отключаем HTML парсинг
)

dp = Dispatcher()
dp.include_router(router)
