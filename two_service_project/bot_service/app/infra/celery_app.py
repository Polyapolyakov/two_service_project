from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,  # используем Redis как backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60, # 30 минут
    task_soft_time_limit=25 * 60, # 25 минут
    result_expires=3600,  # результаты хранятся 1 час
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks(["app.tasks"])
