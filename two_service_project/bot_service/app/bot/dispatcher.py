from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from app.core.config import settings
from app.bot.handlers import router

# Создаем бота
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    parse_mode=ParseMode.HTML
)

# Создаем диспетчер и подключаем роутер
dp = Dispatcher()
dp.include_router(router)