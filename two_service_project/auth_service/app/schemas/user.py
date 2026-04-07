from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserPublic(BaseModel):
    """Публичная схема пользователя (без пароля)."""

    id: int
    email: EmailStr
    role: str
    created_at: datetime

    # Конфигурация для работы FastAPI  с ORM-объектами SQLAlchemy
    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})
