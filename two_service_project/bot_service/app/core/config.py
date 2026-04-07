from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # App settings
    APP_NAME: str = "bot-service"
    ENV: str = "local"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # RabbitMQ (Celery)
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    
    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "stepfun/step-3.5-flash:free"
    OPENROUTER_SITE_URL: str = "https://example.com"
    OPENROUTER_APP_NAME: str = "bot-service"

settings = Settings()
