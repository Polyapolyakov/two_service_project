# Двухсервисная система LLM-консультаций:
**Важное примечание для пользователей из России** :
- Telegram в России работает с ограничениями, для корректной работы бота может потребоваться использование VPN на стороне пользователя;
- серверная часть проекта запускается в облаке GitHub Codespaces и не требует VPN для своей работы.

# Описание проекта:
Проект представляет собой распределенную систему из двух независимых сервисов:

1) Auth Service (FastAPI):
- регистрация и аутентификация пользователей;
- выпуск JWT токенов (sub, role, iat, exp);
- хранение пользователей в SQLite;
- Swagger документация: http://localhost:8000/docs.

2) Bot Service (aiogram + Celery):
- Telegram бот с JWT-авторизацией;
- асинхронная обработка запросов через RabbitMQ;
- хранение токенов в Redis;
- интеграция с OpenRouter LLM.

# Структура проекта:
Была создана корневая папка проекат " two_service_project", в корой созданы две папки «auth_service» и «bot_service» для реализации каждого из сервисов отдельно, в этих папках реализованы следующие папки и функционал:

**Папка «auth_service»:**

1) Параметры инициализации проекта (pyproject.toml) и переменные окружения (.env.example - пример и .env - основной файл, помещенный в .gitignore), а также файл «pytest.ini» (настройки pytest).

2) Папка "app" с файлами init.py и main.py (точка входа в приложение), а также содержащая папки:
- папка «core» с файлами: __init__.py, config.py, security.py и exceptions.py - ядро приложения;
- папка «db» с файлами: __init__.py, base.py, session.py и models.py - база данных;
- папка «schemas» с файлами: __init__.py, auth.py и user.py - pydantic схемы (DTO);
- папка «repositories» с файлами: __init__.py и users.py - - слой доступа к данным;
- папка «usecases» с файлами:__init__.py и auth.py - бизнес-логика;
- папка «api» с файлами: __init__.py, deps.py, routes_auth.py и router.py - HTTP эндпоинты.

3) Папка «tests» с файлами: __init__.py, conftest.py, test_security.py и test_api.py - тестирование приложения.

**Папка «bot_service»:**

1) Параметры инициализации проекта (pyproject.toml) и переменные окружения (.env.example - пример и .env - основной файл, помещенный в .gitignore), а также файл «pytest.ini» (настройки pytest).

 2) Папка "app" с файлами init.py и main.py (точка входа в приложение), а также содержащая папки:
- папка «core» с файлами: __init__.py, config.py и jwt.py - - ядро приложения;
- папка «infra» с файлами: __init__.py, redis.py и celery_app.py – инфраструктурный слой;
- папка «tasks» с файлами: __init__.py и llm_tasks.py – Celery задачи;
- папка «services» с файлами: __init__.py и openrouter_client.py – клиент для OpenRouter API;
- попка «bot» с файлами:__init__.py, dispatcher.py и handlers.py – Telegram бот.

3) Папка «tests» с файлами: __init__.py, conftest.py, test_jwt.py, test_handlers.py и test_openrouter.py - тестирование приложения.

# Запуск приложений (сценарий работы):
**Терминал 1: Запуск Redis (хранение токенов)**
- sudo apt-get install -y redis-server
- sudo service redis-server start
- redis-cli ping # должен ответить: PONG

**Терминал 2: Запуск RabbitMQ (очередь с сообщениями):**
- sudo apt-get update
- sudo apt-get install -y rabbitmq-server
- sudo service rabbitmq-server start
- перейдите по http://localhost:15672 #login: guest / guest

**Терминал 3: Auth Service:**
- cd auth_service
- source .venv/bin/activate
- uv pip install -r <(uv pip compile pyproject.toml)
- uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
- перейдите по http://localhost:8000/docs

**Терминал 4: Celery worker:**
- cd bot_service
- source .venv/bin/activate
- uv pip install -r <(uv pip compile pyproject.toml)
- celery -A app.infra.celery_app worker --loglevel=info

**Терминал 5: Bot Service:**
- cd bot_service
- source .venv/bin/activate
- uv pip install -r <(uv pip compile pyproject.toml)
- uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
- перейдите по http://localhost:8001/health

Далее в приложении «Телеграмм» найдите бота t.me/polyakova_project_bot и начните работу, используя инструкции бота.

# Результаты тестов:
1) Auth Service:
![alt text](image.png)

2) Bot Service:
![alt text](image-1.png)

# Демонстрация работы:
1) Swagger Auth Service (документация):
![alt text](image-2.png)
![alt text](image-4.png)
![alt text](image-6.png)

{<br>
  "email": "polyakova@email.com",<br>
  "password": "123456"<br>
}

![alt text](image-7.png)
![alt text](image-8.png)

{<br>
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NzU1ODc3NjcsImlhdCI6MTc3NTU4NDE2N30.3Pwhy9q-dbWg7NFQK2ebbK0BE5xIRAy3IRdlOEdadrI",<br>
  "token_type": "bearer"<br>
}

![alt text](image-9.png)
![alt text](image-10.png)
![alt text](image-11.png)
![alt text](image-12.png)

2) Telegram бот (пользователь отправляет токен, затем задает вопрос и получает ответ):
![alt text](image-13.png)
![alt text](image-14.png)

3) RabbitMQ интерфейс (активные очереди и сообщения):
![alt text](image-15.png)
![alt text](image-16.png)
![alt text](image-17.png)
![alt text](image-18.png)
![alt text](image-20.png)
![alt text](image-21.png)
![alt text](image-22.png)