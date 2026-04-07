from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Конфигурация приложения, загружаемая из .env"""

    # Чтение переменных окружения из файла .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App настройки
    APP_NAME: str = "auth-service"
    ENV: str = "local"

    # JWT настройки
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database (путь к SQLite)
    SQLITE_PATH: str = "./auth.db"

# Создаем единственный экземпляр для импорта в других частях проекта
settings = Settings()
