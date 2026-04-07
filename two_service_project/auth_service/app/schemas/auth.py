from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Email в формате surname@email.com (например: ivanov@email.com)")
    password: str = Field(..., min_length=6, description="Пароль не короче 6 символов")
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """
        Проверяет, что email соответствует формату surname@email.com.
        """
        # Паттерн: локальная часть + @email.com
        pattern = r'^[a-zA-Z0-9_]+@email\.com$'
        
        if not re.match(pattern, v):
            raise ValueError(
                'Email должен быть в формате surname@email.com.'
                'Пример: ivanov@email.com'
            )
        
        # Дополнительная проверка: имя не должно быть пустым
        local_part = v.split('@')[0]
        if not local_part:
            raise ValueError('Имя пользователя в email не может быть пустым')
        
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
