# 🪐 Universal AI Agent Configuration & Memory Framework

Универсальный модульный фреймворк конфигурации для **Google Antigravity (AGY)**, **Claude Code**, **Cursor** и других AI-агентов. Оптимизирован для **Backend-разработки на Python (FastAPI)** в среде **Windows (PowerShell)** и **Linux/macOS (bash)** с разделением на **публичный фреймворк**, **личный репозиторий памяти** и **корпоративный рабочий контур**.

---

## ⚡ Быстрый запуск (Quick Start)

Все шаги автоматизированы установщиком. Подготовка занимает меньше 2 минут:

### 1. Клонирование репозитория
```powershell
git clone https://github.com/cwerti/agy-conf.git D:\uriit\agy-conf
cd D:\uriit\agy-conf
```

### 2. Запуск автоматического инсталлятора
```powershell
.\scripts\install.ps1 -GlobalOnly
```

Инсталлятор в интерактивном режиме:
1. **Проверит `.env`**: если файла нет, запросит параметры (URL личного репозитория памяти, токены GitHub/GitLab/YouTrack, параметры PostgreSQL и Redis) и безопасно сохранит их в `.env`.
2. **Склонирует личный репозиторий памяти**: если задан `AGENT_MEMORY_REPO_URL`, автоматически склонирует его рядом (`../agent-memory`).
3. **Безопасно объединит MCP-серверы**: запустит [`scripts/merge_mcp_config.py`](file:///D:/uriit/agy-conf/scripts/merge_mcp_config.py), создаст бэкап и бережно объединит серверы в `~/.gemini/config/mcp_config.json`, **никогда не удаляя** существующие серверы пользователя.
4. **Установит хуки безопасности и памяти**: зарегистрирует глобальные `PreToolUse` (контроль команд и защита от утечки секретов) и `PreInvocation` (автоматическая подгрузка памяти) хуки.
5. **Построит локальный поисковый индекс памяти FTS5** для мгновенного поиска без LLM-вызовов.

*(Для Linux / macOS используйте `./scripts/install.sh`)*.

### 3. Удобные шорткаты в PowerShell
Загрузите алиасы для текущей сессии:
```powershell
. .\scripts\profile_alias.ps1
```
*(Или добавьте строку `. 'D:\uriit\agy-conf\scripts\profile_alias.ps1'` в свой `$PROFILE` для постоянного доступа)*.

Доступные шорткаты:
* `agy-mem "<поиск>"` — быстрый поиск по всей базе памяти (FTS5 BM25).
* `agy-log "<тема>" "<цель>"` — фиксация сессии с автоматическим извлечением фактов и синхронизацией в GitHub.
* `agy-db` — автоопределение и переключение строки БД для MCP.
* `agy-sync` — быстрая синхронизация репозитория конфигураций.
* `agy-doc` — запуск комплексной диагностики окружения (`env-doctor`).

---

## 🏛️ Двухрепозиторная архитектура (Dual-Repository Architecture)

Для того чтобы конфигурации и правила оставались **открытыми и переиспользуемыми** для других разработчиков, а личные заметки, контекст рабочих проектов и корпоративные детали оставались **строго приватными**, система разделена на два репозитория:

| Репозиторий | Назначение | Доступ | Что хранится |
| :--- | :--- | :--- | :--- |
| **[`cwerti/agy-conf`](https://github.com/cwerti/agy-conf)** *(Этот репозиторий)* | **Публичный фреймворк конфигураций** | Public / Shared | Универсальные правила (`rules/`), навыки (`skills/`), блюпринты субагентов (`subagents/`), MCP серверы, хуки безопасности и скрипты установки. Чист от личных логов и приватных данных. |
| **[`cwerti/agent-memory`](https://github.com/cwerti/agent-memory)** | **Персональный репозиторий памяти** | Private | Личный профиль разработчика (`context.md`), типизированные знания (`knowledge/*.jsonl`), журналы сессий (`sessions/*.md`), оверрайды настроек. |

### Как это устроено:
* Скрипты памяти ([`scripts/memory_index.py`](file:///D:/uriit/agy-conf/scripts/memory_index.py), [`scripts/memory_recall.py`](file:///D:/uriit/agy-conf/scripts/memory_recall.py), [`scripts/record_session.py`](file:///D:/uriit/agy-conf/scripts/record_session.py)) динамически разрешают путь к памяти:
  1. `AGENT_MEMORY_PATH` (в `.env`: например, `D:\uriit\agent-memory`)
  2. Соседняя папка `../agent-memory`
  3. `~/.gemini/agent-memory`
  4. Локальный фоллбэк: `memory/` внутри `agy-conf` (шаблоны)
* При записи сессии (`record_session.py --push`) коммит и `git push` происходят **только внутри репозитория памяти**, отправляя данные в `https://github.com/cwerti/agent-memory.git`. Репозиторий `agy-conf` остаётся чистым.

---

## 🧠 Долгосрочная типизированная память (Git-Based Agent Memory)

Реализована по мотивам передовых исследований лета 2026 года (*"Why Git Is the Memory Solution for the ADLC"* — arXiv:2607.14390, *"GitOfThoughts"* — arXiv:2606.14470, *"CommitDistill"* — arXiv:2605.18284):

```text
agent-memory/
├── context.md                   # Tier 1: Профиль разработчика, стек, текущие проекты (< 150 строк)
├── knowledge/                   # Tier 2: Типизированные знания (JSONL в Git)
│   ├── facts.jsonl              # Проверенные факты окружения (порты, инструменты)
│   ├── decisions.jsonl          # Архитектурные решения (ADR: вопрос, решение, обоснование)
│   ├── patterns.jsonl           # Паттерны кодовой базы, структура репозиториев
│   └── errors.jsonl             # Решённые сложные ошибки и их фиксы
├── sessions/                    # Tier 3: Хронологические журналы сессий (YYYY-MM-DD-*.md)
└── index/                       # Локальный кеш (в .gitignore)
    └── memory.db                # SQLite FTS5 (BM25) полнотекстовый индекс
```

### Автоматизация памяти:
1. **Автономный Recall при старте сессии**:
   Через `PreInvocation` хук ([`scripts/memory_recall.py`](file:///D:/uriit/agy-conf/scripts/memory_recall.py)) агент на 1-м шаге сессии автоматически получает ключевые архитектурные решения и проверенные факты как эфемерное системное сообщение. На последующих шагах хук возвращает 0 токенов расхода.
2. **Мгновенный локальный поиск (без LLM)**:
   ```powershell
   python scripts/memory_index.py search "postgres"
   # или через шорткат:
   agy-mem "субагент"
   ```
3. **Автономное извлечение знаний при фиксации**:
   При запуске `record_session.py` скрипт автоматически парсит текст сессии, извлекает факты и решения в `knowledge/*.jsonl`, пересобирает индекс и пушит в GitHub.

---

## 📁 Структура каталогов `agy-conf`

```text
agy-conf/
├── AGENTS.md                  # Универсальный мастер-стандарт для всех AI-агентов
├── GEMINI.md                  # Точка входа для Google Antigravity & Gemini CLI
├── CLAUDE.md                  # Точка входа для Claude Code
├── .cursorrules               # Точка входа для Cursor IDE
├── .gitignore                 # Игнорирование персональных сессий, секретов и SQLite DB
├── .env.example               # Шаблон переменных с поддержкой AGENT_MEMORY_PATH
│
├── rules/                     # Модульная библиотека правил
│   ├── general.md             # Общие стандарты коммуникации и точности
│   ├── fastapi.md             # Pydantic v2, async DB, non-blocking I/O, специфика Windows UTF-8
│   ├── workspaces.md          # Разделение аgy-conf vs agent-memory, GitLab vs GitHub
│   ├── memory.md              # Трёхуровневая архитектура типизированной памяти
│   ├── security.md            # Защита секретов, учетных данных и командные запреты
│   ├── git.md                 # Conventional Commits, защита веток
│   ├── subagents.md           # Протокол динамической активации субагентов
│   └── code-quality.md        # Тестирование, линтинг (Ruff, Mypy), типизация
│
├── skills/                    # Навыки агентов (Agent Skills Spec)
│   ├── config-architect/      # Интерактивный AI-консультант для архитектуры репозитория
│   ├── session-journal/       # Автономная фиксация сессий в личный agent-memory
│   ├── mcp-manager/           # Безопасное слияние MCP и смена строк БД
│   ├── env-doctor/            # Комплексная диагностика окружения и шлюза безопасности
│   ├── env-sync/              # Синхронизация между рабочими машинами
│   └── youtrack-helper/       # Интеграция с корпоративным JetBrains YouTrack
│
├── subagents/                 # Каталог специализированных субагентов
│   ├── code-reviewer/         # Ревью кода, Pydantic v2, N+1 queries, безопасность
│   ├── database-architect/    # Миграции Alembic, анализ индексов и планов EXPLAIN
│   ├── api-tester/            # Автоматизация тестов FastAPI (pytest-asyncio, httpx)
│   └── debugger/              # Отладка трейсбеков и логов в изолированном воркспейсе
│
├── mcp/                       # Model Context Protocol
│   ├── mcp_config.json        # Конфигурация MCP для Antigravity
│   └── servers.md             # Описание и настройка серверов
│
├── memory/                    # Шаблоны и точка монтирования памяти
│   ├── README.md              # Документация по подключению личной памяти
│   └── context.example.md     # Шаблон контекста разработчика для новых пользователей
│
├── security/                  # Политики безопасности и перехватчики
│   ├── commands.json          # Allowlist, Denylist и правила подтверждения команд
│   ├── check_command.py       # Валидатор команд (PreToolUse хук)
│   ├── check_secrets.py       # Защита от утечки токенов при записи файлов
│   └── hooks.json             # Конфигурация хуков Antigravity
│
└── scripts/                   # Автоматизация и утилиты
    ├── install.ps1            # Интерактивный установщик (Windows)
    ├── install.sh             # Интерактивный установщик (Linux/macOS)
    ├── merge_mcp_config.py    # Безопасный мерджер MCP без затирания пользовательских серверов
    ├── memory_index.py        # SQLite FTS5 (BM25) индекс и поиск по памяти
    ├── memory_recall.py       # PreInvocation хук для инжекции активных знаний в сессию
    ├── record_session.py      # Автономный логгер сессий с пушем в agent-memory
    ├── update_db_connection.py# Автоопределение и переключение строки БД для MCP
    └── profile_alias.ps1      # Шорткаты для PowerShell (agy-mem, agy-log, agy-db...)
```

---

## 👥 Специализированные субагенты (Subagents)

В Antigravity субагенты определяются сессионно через инструмент `define_subagent` на основе шаблонов в `subagents/<имя>/subagent.json`:

| Субагент | Роль | Инструменты | Когда применять |
| :--- | :--- | :--- | :--- |
| **`code-reviewer`** | Senior Python & FastAPI Reviewer | **Read-Only** (код, MCP) | Аудит перед коммитом: проверка Pydantic v2, non-blocking I/O, N+1 queries. |
| **`database-architect`** | PostgreSQL & SQLAlchemy 2.0 Specialist | **Read + Write** (миграции, MCP) | Анализ и генерация миграций Alembic, `EXPLAIN ANALYZE`, оптимизация индексов. |
| **`api-tester`** | QA Automation Engineer | **Read + Write** (файлы тестов, pytest) | Автоматизация тестов FastAPI: асинхронные тесты (`pytest-asyncio`, `httpx`). |
| **`debugger`** | Senior Backend Troubleshooter | **Read + Write** (файлы, тесты, логи) | Глубокий анализ логов и трейсбеков в изолированном воркспейсе. |

### Примеры вызова в чате:
* *"Запусти code-reviewer для проверки изменений перед созданием MR"*
* *"Пусть database-architect проверит сгенерированную миграцию"*
* *"Поручи api-tester написать тесты для эндпоинта аутентификации"*

---

## 🔌 Инструменты MCP (Model Context Protocol)

Все серверы используют стандартный `npx` или Python и безопасно объединяются с существующими настройками через [`scripts/merge_mcp_config.py`](file:///D:/uriit/agy-conf/scripts/merge_mcp_config.py):

* **`fetch`**: Выполнение реальных HTTP-запросов к локальному FastAPI, проверка OpenAPI и эндпоинтов.
* **`postgres-dev`**: Чтение структуры таблиц, колонок, индексов и запуск `EXPLAIN ANALYZE`.
* **`redis-dev`**: Инспекция ключей кэша, сессий и очередей задач.
* **`docker`**: Статус контейнеров (`docker compose ps`) и чтение логов упавших сервисов.
* **`gitlab-work`**: Интеграция с корпоративным self-hosted GitLab (`GITLAB_URL`, `GITLAB_TOKEN`).
* **`github-personal`**: Интеграция с личным GitHub (`GITHUB_TOKEN`).
* **`filesystem`**: Быстрый доступ и индексация рабочего пространства.

---

## 🛡️ Безопасность и фильтрация команд

Политика в [`security/commands.json`](file:///D:/uriit/agy-conf/security/commands.json) контролируется хуком [`security/check_command.py`](file:///D:/uriit/agy-conf/security/check_command.py):

* 🔴 **Denylist (Заблокировано без исключений)**:
  * Деструктивные команды: `rm -rf /`, `rmdir /s /q C:\`, `del /s C:\`, `format`.
  * Непроверенный запуск скриптов из сети: `curl ... | sh`, `iwr ... | iex`.
  * Сброс схемы БД: `alembic downgrade base`.
  * Принудительный пуш: `git push --force` в `main`/`master`.
* 🟡 **Require Confirmation (Требуется подтверждение пользователя)**:
  * `git push` в **корпоративный GitLab**.
  * Накат миграций на базу: `alembic upgrade head`.
  * Установка пакетов: `pip install`, `poetry add/install`, `npm i -g`.
  * Деструктивные действия с контейнерами: `docker compose down -v`, `docker system prune`.
* 🟢 **Allowlist (Разрешено автоматически без диалогов)**:
  * `git push` в **личный репозиторий памяти** (`agent-memory`) и личный GitHub.
  * Чтение git: `git status`, `git log`, `git diff`, `git branch`.
  * Инспекция файлов: `ls`, `dir`, `Get-ChildItem`, `cat`, `Get-Content`.
  * Проверка версий: `python --version`, `node -v`, `git --version`, `poetry --version`.
  * Тесты и линтеры: `pytest`, `poetry run pytest`, `ruff check`, `mypy`.
  * Безопасная инспекция миграций: `alembic current`, `alembic heads`, `alembic history`.

---

## 🔗 Подключение к проектам

Чтобы применить правила и шлюз безопасности к любому проекту разработки:

```powershell
.\scripts\install.ps1 -ProjectDir "D:\uriit\my-backend-app"
```

В целевом проекте будет создана папка `.agents/` с перехватчиком `hooks.json`, а также симлинки/копии на `AGENTS.md` и `GEMINI.md`.
