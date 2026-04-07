from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.router import router as api_router 


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup: создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: закрываем соединения
    await engine.dispose()


def create_app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Подключаем роутеры
    app.include_router(api_router)
    
    # Health check (можно оставить здесь или вынести в отдельный роутер)
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok",
                    "service": settings.APP_NAME,
                    "environment": settings.ENV,
                    "version": "0.1.0"
        }

    return app


app = create_app()
