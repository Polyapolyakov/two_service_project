from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings

# Формируем строку подключения для асинхронной SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"

# Движок базы данных для фабрики сессий
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False, 
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
