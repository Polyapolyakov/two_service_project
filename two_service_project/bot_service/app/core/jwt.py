from jose import jwt
from app.core.config import settings

def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Токен истек")
    except jwt.JWTError:
        raise ValueError("Невалидный токен")
