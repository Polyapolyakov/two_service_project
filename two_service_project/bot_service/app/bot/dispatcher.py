from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from app.core.config import settings
from app.bot.handlers import start, token, message

# Создаем бота
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    parse_mode=ParseMode.HTML
)

# Создаем диспетчер
dp = Dispatcher()

# Регистрируем роутеры
dp.include_router(start.router)
dp.include_router(token.router)
dp.include_router(message.router)
