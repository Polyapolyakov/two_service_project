"""
Настройка бота и диспетчера Telegram.
"""
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from app.core.config import settings
from app.bot.handlers import router

# Создаем бота с новым синтаксисом (aiogram 3.7+)
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Создаем диспетчер и подключаем роутер
dp = Dispatcher()
dp.include_router(router)