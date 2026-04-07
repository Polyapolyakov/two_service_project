from fastapi import APIRouter
from app.api import routes_auth

# Создаем главный роутер
router = APIRouter()

# Подключаем все подроутеры
router.include_router(routes_auth.router)
