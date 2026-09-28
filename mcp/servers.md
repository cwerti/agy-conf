# Model Context Protocol (MCP) Server Catalog

Каталог MCP серверов, сгруппированный по задачам для **Python FastAPI бэкенд-разработки** и командного окружения.

---

## 🛠️ 1. Бэкенд-разработка (FastAPI, Базы данных, Контейнеры)

### 1. `fetch` (Тестирование и проверка API)
* **Зачем нужно**: Позволяет агенту делать реальные HTTP-запросы (GET, POST, PUT, DELETE) к вашему запущенному локально FastAPI-приложению (`http://localhost:8000`), скачивать OpenAPI JSON схему, проверять ответы и валидацию Pydantic.
* **Команда**: `npx -y @modelcontextprotocol/server-fetch`
* **Настройка**: Не требует ключей.

### 2. `postgres-dev` (База данных PostgreSQL)
* **Зачем нужно**:
  * Чтение структуры таблиц, типов колонок, внешних ключей и индексов.
  * Позволяет агенту писать точные SQLAlchemy-модели и SQL-запросы, соответствующие реальной схеме БД.
  * Выполнение `EXPLAIN ANALYZE` для устранения медленных запросов.
* **Команда**: `npx -y @modelcontextprotocol/server-postgres ${DATABASE_URL}`
* **Переменная**: `DATABASE_URL` (например, `postgresql://postgres:postgres@localhost:5432/my_db`).

### 3. `redis-dev` (Кэширование & Очереди задач)
* **Зачем нужно**:
  * Инспекция ключей кэша FastAPI, проверка TTL.
  * Мониторинг очередей задач (Celery, Arq, RQ), содержимого очередей и структуры сериализованных сообщений.
* **Команда**: `npx -y @modelcontextprotocol/server-redis ${REDIS_URL}`
* **Переменная**: `REDIS_URL` (например, `redis://localhost:6379/0`).

### 4. `docker` (Локальный стек и логи контейнеров)
* **Зачем нужно**:
  * Инспекция запущенных сервисов локального окружения (`docker compose ps`).
  * Чтение логов упавшего бэкенда или БД прямо из чата (`docker logs <container_name>`), без переключения в терминал.
* **Команда**: `npx -y @modelcontextprotocol/server-docker`
* **Настройка**: Требует запущенного Docker Desktop / Docker daemon.

### 5. `sentry` (Анализ трейсбеков и ошибок)
* **Зачем нужно**: Агент может подтягивать реальный трейсбек ошибки с продакшена или стейджа, сопоставлять его с кодом в репозитории и сразу предлагать патч.
* **Команда**: `npx -y @modelcontextprotocol/server-sentry`
* **Переменные**: `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`.

---

## 🏢 2. Системы контроля версий и окружение

### 6. `gitlab-work` (Рабочий Self-hosted GitLab)
* **Зачем нужно**: Чтение и создание Merge Requests, веток, просмотр обсуждений код-ревью в вашей корпоративной сети.
* **Команда**: `npx -y @modelcontextprotocol/server-gitlab`
* **Переменные**:
  * `GITLAB_API_URL`: URL вашего корпоративного GitLab (например, `https://gitlab.company.ru/api/v4`).
  * `GITLAB_PERSONAL_ACCESS_TOKEN`: PAT с правами `api`.

### 7. `github-personal` (Личный GitHub)
* **Зачем нужно**: Управление личными репозиториями, Pull Requests и Issues.
* **Команда**: `npx -y @modelcontextprotocol/server-github`
* **Переменная**: `GITHUB_PERSONAL_ACCESS_TOKEN`.

### 8. `filesystem` (Файловая система)
* **Зачем нужно**: Быстрая индексация и поиск файлов в рабочем пространстве `D:\uriit`.
* **Команда**: `npx -y @modelcontextprotocol/server-filesystem D:\uriit`

---

## 🔐 Быстрая настройка переменных в Windows

Чтобы активировать все бэкенд-серверы, достаточно выполнить в PowerShell:

```powershell
[System.Environment]::SetEnvironmentVariable('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/app_db', 'User')
[System.Environment]::SetEnvironmentVariable('REDIS_URL', 'redis://localhost:6379/0', 'User')
[System.Environment]::SetEnvironmentVariable('GITLAB_URL', 'https://gitlab.company.ru/api/v4', 'User')
[System.Environment]::SetEnvironmentVariable('GITLAB_TOKEN', 'glpat-xxxx', 'User')
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_xxxx', 'User')
```
