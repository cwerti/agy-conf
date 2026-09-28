# 🪐 Universal AI Agent Configuration & Memory Repository

Универсальный репозиторий конфигурации для **Google Antigravity (AGY)**, **Claude Code**, **Cursor** и других AI-агентов, оптимизированный для **Backend-разработки на Python (FastAPI)** в среде **Windows (PowerShell)** с разделением на **рабочий контур (Self-hosted GitLab + YouTrack)** и **личный контур (GitHub)**.

---

## 📑 Навигация по разделам
1. [Архитектура репозитория](#-архитектура-репозитория)
2. [Навыки агента (Skills)](#-навыки-агента-skills)
3. [Специализированные субагенты (Subagents)](#-специализированные-субагенты-subagents)
4. [Инструменты MCP (Model Context Protocol)](#-инструменты-mcp-model-context-protocol)
5. [Динамическое переключение БД между проектами](#-динамическое-переключение-бд-между-проектами)
6. [Безопасность и фильтрация команд](#-безопасность-и-фильтрация-команд)
7. [Долгосрочная память агента (Memory & Sessions)](#-долгосрочная-память-агента-memory--sessions)
8. [Правила разработки (Rules)](#-правила-разработки-rules)
9. [Быстрый старт и управление](#-быстрый-старт-и-управление)

---

## 📁 Архитектура репозитория

```text
agy-conf/
├── AGENTS.md                  # Универсальный мастер-стандарт для всех AI-агентов
├── GEMINI.md                  # Точка входа для Google Antigravity & Gemini CLI
├── CLAUDE.md                  # Точка входа для Claude Code
├── .cursorrules               # Точка входа для Cursor IDE
├── .gitattributes             # Принудительная нормализация переносов строк (LF vs CRLF)
├── .gitignore                 # Защита секретов, токенов, .env и локальных оверрайдов
├── .env.example               # Шаблон всех переменных окружения с комментариями
│
├── rules/                     # Модульная библиотека правил
│   ├── general.md             # Общие стандарты коммуникации и точности
│   ├── fastapi.md             # Pydantic v2, async DB, non-blocking I/O, специфика Windows UTF-8
│   ├── workspaces.md          # Разделение рабочего GitLab+YouTrack и личного GitHub
│   ├── memory.md              # Правила автономного ведения журнала решений в memory/
│   ├── security.md            # Защита секретов, учетных данных и командные запреты
│   ├── git.md                 # Conventional Commits, защита main/master
│   └── code-quality.md        # Тестирование, линтинг (Ruff, Mypy), типизация
│
├── skills/                    # Навыки агентов (Agent Skills Spec)
│   ├── config-architect/      # Интерактивный AI-консультант для проектирования конфига
│   ├── add-customization/     # Интерактивное добавление новых правил, скиллов, MCP, команд
│   ├── session-journal/       # Автономная фиксация сессий и решений в личный GitHub
│   ├── mcp-manager/           # Управление MCP и переключение баз данных
│   ├── env-doctor/            # Комплексная диагностика утилит, рантаймов и шлюза безопасности
│   └── env-sync/              # Развертывание и перенос настроек между машинами
│
├── subagents/                 # Специализированные субагенты (Каталог ролей)
│   ├── code-reviewer/         # Ревью кода, Pydantic v2, N+1 queries, безопасность
│   ├── database-architect/    # Миграции Alembic, анализ индексов и планов EXPLAIN
│   ├── api-tester/            # Автоматизация тестов FastAPI (pytest-asyncio, httpx)
│   └── debugger/              # Глубокая отладка трейсбеков и логов в изолированном контексте
│
├── mcp/                       # Model Context Protocol
│   ├── mcp_config.json        # Активный конфигурационный файл серверов
│   ├── mcp_config.example.json# Каталог готовых серверов (БД, кэш, докер, гитлаб, ютрек)
│   └── servers.md             # Подробная документация по настройке и токенам
│
├── memory/                    # Долгосрочная память агента (Persistent Memory)
│   ├── context.md             # Компактный индекс профиля разработчика, стека и активных проектов
│   └── sessions/              # Хронологические журналы сессий (YYYY-MM-DD-<topic>.md)
│
├── security/                  # Политики и шлюз безопасности
│   ├── commands.json          # Allowlist, Denylist и Require-Confirmation
│   ├── check_command.py       # Кроссплатформенный валидатор команд (AGY PreToolUse хук)
│   ├── check_secrets.py       # Валидатор защиты от утечки токенов при редактировании файлов
│   └── hooks.json             # AGY хуки перехвата команд и записи файлов
│
├── scripts/                   # Автоматизация и утилиты
│   ├── install.ps1            # Интерактивный установщик с опросом .env для Windows
│   ├── install.sh             # Интерактивный установщик для Linux / macOS
│   ├── sync.ps1               # Быстрая синхронизация с Git (Windows)
│   ├── sync.sh                # Быстрая синхронизация с Git (Linux / macOS)
│   ├── update_db_connection.py# Автоопределение и обновление DATABASE_URL для MCP
│   ├── record_session.py      # Скрипт записи логов сессий в memory/
│   ├── youtrack_client.py     # Легковесный клиент для чтения и комментирования YouTrack
│   └── profile_alias.ps1      # Шорткаты для PowerShell профиля (agy-db, agy-sync, agy-yt...)
│
├── .githooks/                 # Локальные Git-хуки
│   ├── pre-commit             # Проверка файлов на утечку секретов и линтинг Ruff перед коммитом
│   └── commit-msg             # Контроль формата Conventional Commits
│
└── templates/                 # Шаблоны для подключения к проектам
    ├── .agents/hooks.json     # Локальный перехватчик для проектов
    └── fastapi-boilerplate/   # Готовый боевой шаблон сервиса (FastAPI, async DB, Docker)
```

---

## 🧠 Навыки агента (Skills)

Каждый навык расположен в `skills/<имя>/SKILL.md` и активируется агентом автономно или по вашей команде:

| Навык | Когда активируется / Что делает | Как вызвать вручную |
| :--- | :--- | :--- |
| **`config-architect`** | **Интерактивный архитектор-консультант**: обсуждает с вами идеи по развитию конфига, предлагает варианты (Rule vs Skill vs MCP vs Hook), оценивает расход токенов и готовит изменения. | *"Помоги настроить конфиг"*, *"Хочу обсудить добавление Celery"* |
| **`youtrack-helper`** | **Интеграция с YouTrack**: выгружает описание задачи, Acceptance Criteria и комментарии коллег, создает ветку под задачу. | *"Покажи задачу PROJ-123"*, *"Что в тикете TASK-42"* |
| **`add-customization`** | Добавляет в репозиторий новые правила (`rules/`), навыки (`skills/`), серверы MCP или команды в `commands.json`. Проверяет синтаксис и сразу тестирует регулярные выражения. | *"Добавь правило для Celery"*, *"Добавь команду в allowlist"* |
| **`session-journal`** | Формирует структурированный отчет по сессии (цель, принятые решения, измененные файлы, следующие шаги), сохраняет в `memory/sessions/` и пушит в личный GitHub. | *"Зафиксируй сессию"*, *"Сохрани решения в память"* |
| **`mcp-manager`** | Безопасно настраивает MCP-серверы, проверяет доступность утилит и динамически переключает URL баз данных между проектами. | *"Проверь статус MCP"*, *"Смени БД для проекта"* |
| **`env-doctor`** | Диагностирует систему: проверяет доступность Python, Node, Git, Docker, валидирует работу хуков безопасности и тестирует тестовые команды. | *"Проверь окружение"*, *"Запусти doctor"* |
| **`env-sync`** | Подтягивает последние изменения из удаленного репозитория и обновляет глобальные симлинки/копии в `~/.gemini/config/`. | *"Синхронизируй настройки"* |

---

## 👥 Специализированные субагенты (Subagents)

Субагенты — это специализированные копии агента с изолированным контекстом и собственной экспертной ролью. Они запускаются параллельно в фоне, решая узкие задачи без захламления основного диалога и перерасхода токенов:

| Субагент | Экспертиза / Роль | Инструменты | Когда применять |
| :--- | :--- | :--- | :--- |
| **`code-reviewer`** | Senior Python & FastAPI Code Reviewer | **Read-Only** (код, MCP) | Полный аудит перед созданием MR/коммитом: проверка Pydantic v2, отсутствие sync I/O, N+1 queries, строгая типизация. |
| **`database-architect`** | PostgreSQL & SQLAlchemy 2.0 Specialist | **Read + Write** (миграции, MCP) | Анализ и генерация миграций Alembic, аудит медленных запросов (`EXPLAIN ANALYZE`), проектирование индексов и защита от локов. |
| **`api-tester`** | QA Automation Engineer (Pytest) | **Read + Write** (файлы тестов, pytest) | Автоматизация тестов FastAPI: асинхронные тесты (`pytest-asyncio`, `httpx`), валидация HTTP 422, негативные сценарии. |
| **`debugger`** | Senior Backend Troubleshooter | **Read + Write** (файлы, тесты, логи) | Глубокий анализ трейсбеков ошибок, логов контейнеров Docker, поиск причин плавающих багов в изолированном воркспейсе. |

### Как вызывать субагентов
Вы можете поручить задачу напрямую:
* *"Запусти code-reviewer для проверки последних изменений"*
* *"Пусть database-architect проверит сгенерированную миграцию"*
* *"Поручи api-tester написать интеграционные тесты для роута /auth"*
* *"Подключи debugger для разбора ошибки в логах"*

---

## 🔌 Инструменты MCP (Model Context Protocol)

Все серверы в [`mcp/mcp_config.json`](file:///D:/uriit/agy-conf/mcp/mcp_config.json) работают через стандартный `npx` (без привязки к `uv`):

### 1. Бэкенд и инфраструктура (FastAPI)
* **`fetch`**: Позволяет агенту слать реальные HTTP-запросы (GET, POST, PUT, DELETE) к запущенному локально FastAPI (`http://localhost:8000`), скачивать OpenAPI спецификацию и проверять валидацию Pydantic на живом бэкенде.
* **`postgres-dev`**: Читает реальную структуру таблиц, колонок, индексов и внешних ключей в PostgreSQL, а также выполняет `EXPLAIN ANALYZE` для оптимизации запросов SQLAlchemy.
* **`redis-dev`**: Инспектирует ключи кэша, TTL, сессии и состояние очередей задач (Celery / Arq / RQ).
* **`docker`**: Показывает статус контейнеров локального dev-стека (`docker compose ps`) и читает логи упавших сервисов прямо в чат.

### 2. Контроль версий и файловая система
* **`gitlab-work`**: Подключение к корпоративному self-hosted GitLab через переменные `GITLAB_URL` и `GITLAB_TOKEN` (чтение/создание MR, issues, веток, комментирование код-ревью).
* **`github-personal`**: Подключение к личному GitHub через `GITHUB_TOKEN`.
* **`filesystem`**: Быстрый доступ и индексация рабочего пространства `D:\uriit`.

---

## 🗄️ Динамическое переключение БД между проектами

Вам **не нужно** вручную редактировать конфиги при смене проекта:

1. **Автоопределение**:
   Скрипт сам находит строку подключения в `.env`, `alembic.ini` или `config.py` проекта:
   ```powershell
   python scripts/update_db_connection.py --auto-detect "D:\uriit\my-app"
   ```
2. **Автоматическая нормализация драйверов**:
   Если в проекте указан асинхронный драйвер `postgresql+asyncpg://...`, скрипт автоматически преобразует его в чистый `postgresql://...`, понятный Node.js MCP-серверу.
3. **Автовосстановление при ошибке**:
   Если агент пытается обратиться к БД через MCP и получает ошибку (Connection refused, DB does not exist):
   * Агент сам спрашивает актуальный `DATABASE_URL`.
   * Сам запускает `python scripts/update_db_connection.py "<url>"`.
   * Конфигурация MCP в `~/.gemini/config/mcp_config.json` и переменная окружения Windows обновляются мгновенно.

---

## 🛡️ Безопасность и фильтрация команд

Политика в [`security/commands.json`](file:///D:/uriit/agy-conf/security/commands.json) контролируется скриптом [`security/check_command.py`](file:///D:/uriit/agy-conf/security/check_command.py):

* 🔴 **Denylist (Жестко заблокировано везде)**:
  * Удаление системных дисков/корня: `rm -rf /`, `rmdir /s /q C:\`, `del /s C:\`.
  * Форматирование дисков: `format`, `mkfs`, `dd if=`.
  * Непроверенный запуск скриптов из сети: `curl ... | sh`, `iwr ... | iex`.
  * Полный сброс схемы БД: `alembic downgrade base`.
  * Принудительный пуш в основные ветки: `git push --force` в `main`/`master`.
* 🟡 **Require Confirmation (Требуется подтверждение)**:
  * `git push` в **корпоративный GitLab**.
  * Накат миграций на базу: `alembic upgrade head`.
  * Установка пакетов: `pip install`, `poetry add/install`, `npm i -g`.
  * Деструктивные действия с контейнерами: `docker compose down -v`, `docker system prune`.
* 🟢 **Allowlist (Разрешено автоматически)**:
  * `git push` в **личный репозиторий памяти** (совпадающий с `AGENT_MEMORY_REPO_URL` или репозиторий `agy-conf`).
  * Чтение git: `git status`, `git log`, `git diff`, `git branch`.
  * Инспекция файлов: `ls`, `dir`, `Get-ChildItem`, `cat`, `Get-Content`.
  * Проверка версий: `python --version`, `node -v`, `git --version`, `poetry --version`.
  * Тесты и линтеры: `pytest`, `poetry run pytest`, `ruff check`, `mypy`, `black --check`.
  * Безопасная инспекция миграций: `alembic current`, `alembic heads`, `alembic history`.

---

## 🧠 Долгосрочная память агента (Memory & Sessions)

Позволяет сохранять контекст между сессиями без повторного объяснения архитектуры и расхода токенов:

1. **Глобальный контекст: [`memory/context.md`](file:///D:/uriit/agy-conf/memory/context.md)**:
   * Профиль разработчика, используемый стек (Windows, FastAPI, PostgreSQL, без `uv`).
   * Разделение на корпоративный контур (GitLab + YouTrack) и личный (GitHub).
   * Список ключевых принятых решений (ADR).
2. **Журнал сессий: [`memory/sessions/`](file:///D:/uriit/agy-conf/memory/sessions/)**:
   * Датированные файлы `YYYY-MM-DD-<тема>.md`.
   * Агент автоматически фиксирует ход работы, аргументы за/против выбранных библиотек и список измененных файлов.
3. **Синхронизация**:
   * Переменная `AGENT_MEMORY_REPO_URL` задает целевой репозиторий.
   * `git push` в этот репозиторий **разрешен агенту автоматически** — агент сам сохраняет свои отчеты без диалогов подтверждения.

---

## 📜 Правила разработки (Rules)

* **[`rules/fastapi.md`](file:///D:/uriit/agy-conf/rules/fastapi.md)**:
  * Pydantic v2 (`ConfigDict`, строгие DTO).
  * Async сессии SQLAlchemy 2.0 через `Depends(get_db)` с безопасным commit/rollback.
  * Запрет блокирующего I/O в `async def` (только `asyncio.sleep`, `httpx.AsyncClient`).
  * **Windows**: обязательное указание `encoding="utf-8"` при работе с файлами (защита от крашей CP1251) и использование `pathlib.Path`.
* **[`rules/workspaces.md`](file:///D:/uriit/agy-conf/rules/workspaces.md)**:
  * Разделение рабочих и личных коммитов через `includeIf` в `~/.gitconfig`.
  * Привязка задач YouTrack к коммитам (`feat(TASK-123): ...`).
  * Запрет на попадание корпоративных ссылок и токенов в личный GitHub.
* **[`rules/security.md`](file:///D:/uriit/agy-conf/rules/security.md)**:
  * Запрет на хардкод секретов, токенов и паролей в коде.

---

## 🚀 Быстрый старт и управление

### 1. Первоначальная установка на Windows

Запустите скрипт установки в PowerShell:

```powershell
.\scripts\install.ps1 -GlobalOnly
```

1. Скрипт проверит наличие `.env`. Если его нет, он прочитает [`.env.example`](file:///D:/uriit/agy-conf/.env.example) и **интерактивно запросит в терминале** все необходимые переменные:
   * `AGENT_MEMORY_REPO_URL` (ссылка на ваш личный GitHub репозиторий)
   * Токены GitLab, YouTrack, GitHub
   * Строки подключения к PostgreSQL и Redis
2. Нажмите `Enter`, чтобы принять значение по умолчанию, или введите своё.
3. Скрипт предложит применить переменные в профиль Windows User (`[Y/n]`).
4. Свяжет MCP-конфигурацию с Antigravity (`~/.gemini/config/mcp_config.json`) и проверит работу шлюза безопасности.

*(Если потребуется заново пройти опрос: `.\scripts\install.ps1 -Reconfigure`)*.

---

### 2. Подключение правил и хуков к конкретному проекту

Чтобы применить правила и шлюз безопасности к проекту разработки:

```powershell
.\scripts\install.ps1 -ProjectDir "D:\uriit\my-backend-app"
```

В проекте будет создана папка `.agents/` с перехватчиком `hooks.json`, а также файлы `AGENTS.md` и `GEMINI.md`.

---

### 3. Рутинные команды управления

* **Синхронизация репозитория конфигурации**:
  ```powershell
  .\scripts\sync.ps1 -CommitMessage "feat: add celery guidelines"
  ```
* **Переключение базы данных для MCP**:
  ```powershell
  python scripts/update_db_connection.py --auto-detect "D:\uriit\another-project"
  ```
* **Ручная запись сессии в память**:
  ```powershell
  python scripts/record_session.py "fastapi-auth" "Setup JWT authentication" "Used PyJWT and passlib" app/auth.py
  ```
