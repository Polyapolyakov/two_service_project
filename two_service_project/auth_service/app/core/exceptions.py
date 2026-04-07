from fastapi import HTTPException, status

class BaseHTTPException(HTTPException):
    """Базовое исключение для HTTP ошибок."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class UserAlreadyExistsError(BaseHTTPException):
    """Пользователь с таким email уже существует."""
    def __init__(self, detail: str = "Пользователь с таким email уже существует"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class InvalidCredentialsError(BaseHTTPException):
    """Неверные учетные данные."""
    def __init__(self, detail: str = "Неверный email или пароль"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class InvalidTokenError(BaseHTTPException):
    """Невалидный токен."""
    def __init__(self, detail: str = "Недействительный токен"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class TokenExpiredError(BaseHTTPException):
    """Истекший токен."""
    def __init__(self, detail: str = "Токен истек"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class UserNotFoundError(BaseHTTPException):
    """Пользователь не найден."""
    def __init__(self, detail: str = "Пользователь не найден"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class PermissionDeniedError(BaseHTTPException):
    """Доступ запрещен."""
    def __init__(self, detail: str = "Доступ запрещен"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
