"""
Общие фикстуры для всех тестов Auth Service.
"""
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from app.db.base import Base
from app.main import app
from app.api import deps


@pytest.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Фикстура для тестовой БД in-memory.
    """
    # Создаем in-memory SQLite для тестов
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Очищаем после тестов
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура для сессии БД.
    """
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура для HTTP клиента с подмененной зависимостью get_db.
    """
    
    # Подменяем зависимость get_db на нашу тестовую сессию
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[deps.get_db] = override_get_db
    
    # Создаем клиент
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    # Очищаем переопределения
    app.dependency_overrides.clear()
