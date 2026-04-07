from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    await message.answer(
        "Привет! Я бот для работы с LLM.\n\n"
        "Для начала работы вам нужно:\n"
        "1. Зарегистрироваться в Auth Service\n"
        "2. Получить JWT токен через POST /auth/login\n"
        "3. Отправить токен боту командой /token ваш_токен\n\n"
        "После этого вы сможете задавать мне любые вопросы!"
    )


@router.message(Command("token"))
async def cmd_token(message: Message):
    """Обработчик команды /token для сохранения JWT."""
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(
            "Пожалуйста, укажите токен.\n"
            "Пример: /token eyJhbGciOiJIUzI1NiIs..."
        )
        return
    
    token = parts[1].strip()
    
    try:
        payload = decode_and_validate(token)
        user_id = payload.get("sub")
        if not user_id:
            await message.answer("Невалидный токен: отсутствует поле sub")
            return
    except ValueError as e:
        await message.answer(f"Ошибка валидации токена: {str(e)}")
        return
    
    redis = await get_redis()
    key = f"tg_token:{message.from_user.id}"
    await redis.set(key, token, ex=3600 * 24)
    
    await message.answer(
        "Токен успешно сохранен!\n\n"
        "Теперь вы можете отправлять мне любые сообщения, "
        "и я буду отвечать с помощью LLM."
    )


@router.message()
async def handle_message(message: Message):
    """Обработчик обычных текстовых сообщений."""
    # Пропускаем команды
    if message.text and message.text.startswith('/'):
        return
    
    redis = await get_redis()
    key = f"tg_token:{message.from_user.id}"
    token = await redis.get(key)
    
    if not token:
        await message.answer(
            "У вас нет сохраненного токена.\n\n"
            "Пожалуйста, получите токен в Auth Service и отправьте его командой:\n"
            "/token ваш_токен"
        )
        return
    
    try:
        decode_and_validate(token)
    except ValueError as e:
        await message.answer(
            f"Ваш токен недействителен: {str(e)}\n\n"
            "Пожалуйста, получите новый токен и отправьте его командой /token"
        )
        return
    
    # Отправляем задачу в Celery
    llm_request.delay(
        prompt=message.text,
        user_id=message.from_user.id,
        temperature=0.7
    )
    
    await message.answer(
        "Обрабатываю ваш запрос...\n\n"
        "Ответ придет, как только LLM сгенерирует его.\n"
        "Обычно это занимает несколько секунд."
    )
