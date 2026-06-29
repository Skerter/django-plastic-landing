# Переменные окружения

Полный справочник переменных окружения. Конфигурация задаётся через файл
`.env` в корне проекта (читается `django-environ`). Это **единый источник
истины** по переменным — шаблоны `.env.example` (локально) и
`deploy/selectel/.env.prod.example` (прод) ссылаются сюда.

!!! danger "Секреты не коммитятся"
    `.env` добавлен в `.gitignore`. В репозитории хранятся только шаблоны
    `*.example` без реальных значений. Никогда не коммитьте заполненный `.env`.

Колонка **Окружение** показывает, где переменная нужна:
**dev** — локальная разработка, **prod** — сервер, **оба** — везде.

---

## Django

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `DJANGO_SETTINGS_MODULE` | оба | — | Модуль настроек. Локально `config.settings.dev`, на проде `config.settings.prod`. |
| `SECRET_KEY` | оба | — (обязательна) | Криптоключ Django. На проде сгенерировать: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`. |
| `DEBUG` | оба | `False` | Режим отладки. Локально `True`, на проде **строго** `False`. |
| `ALLOWED_HOSTS` | оба | пусто | Список хостов через запятую. Локально `localhost,127.0.0.1`, на проде — домен сайта. |

## База данных

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `DATABASE_URL` | prod | — | URL подключения к Postgres. Хост — имя сервиса compose (`db`), а не `localhost`. |

!!! note "Локально база — SQLite"
    Настройки `dev` жёстко используют SQLite (`db.sqlite3`) и `DATABASE_URL`
    **не читают**. Переменная нужна только на проде (`prod`).

## Postgres (контейнер `db`)

Читаются Docker Compose на проде. Значения должны совпадать с `DATABASE_URL`.

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `POSTGRES_DB` | prod | — | Имя базы (`demoplast`). |
| `POSTGRES_USER` | prod | — | Пользователь БД (`demoplast`). |
| `POSTGRES_PASSWORD` | prod | — | Пароль. Тот же, что в `DATABASE_URL`. |

## Docker Compose

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `COMPOSE_PROJECT_NAME` | prod | имя папки | Имя проекта Compose — фиксирует имена томов. Для проекта `demo-plast`. |
| `SITE_DOMAIN` | prod | — | Домен для маршрутизации Traefik и выпуска TLS-сертификата. |

## Sentry (мониторинг ошибок)

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `SENTRY_DSN` | prod | пусто | DSN проекта на sentry.io. Пусто → Sentry не активируется. |
| `SENTRY_TRACES_SAMPLE_RATE` | prod | `0.2` | Доля трейсов производительности (0.0–1.0). |

!!! note "Персональные данные вырезаются"
    Перед отправкой в Sentry имена, телефоны и e-mail удаляются
    (`config/sentry.py`, `before_send`) — требование 152-ФЗ. См.
    [Соответствие 152-ФЗ](../explanation/compliance-152fz.md).

## Email (SMTP)

Доступ отправителя писем о заявках. Получатель задаётся **в админке**
(SiteSettings → «E-mail для уведомлений»), а не здесь.

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `DEFAULT_FROM_EMAIL` | оба | пусто | Адрес-отправитель. **Должен совпадать** с `EMAIL_HOST_USER`. |
| `EMAIL_HOST` | prod | пусто | SMTP-сервер (`smtp.example.com`). |
| `EMAIL_PORT` | prod | `465` | Порт SMTP (типично 465 для implicit SSL). |
| `EMAIL_HOST_USER` | prod | пусто | Логин SMTP (адрес ящика-отправителя). |
| `EMAIL_HOST_PASSWORD` | prod | пусто | **Пароль приложения** (не обычный пароль). |
| `EMAIL_USE_SSL` | prod | `True` | Implicit SSL (порт 465). |
| `EMAIL_USE_TLS` | prod | `False` | STARTTLS (порт 587). Взаимоисключающа с `EMAIL_USE_SSL`. |

!!! warning "SSL и TLS — взаимоисключающие"
    Одновременно `EMAIL_USE_SSL=True` и `EMAIL_USE_TLS=True` нельзя — Django
    откажется стартовать. Для Яндекса: SSL=True, TLS=False, порт 465.

Локально SMTP не нужен: настройки `dev` печатают письма в консоль. Подробности
настройки — [Каналы уведомлений](../how-to/enable-notification-channels.md).

## Telegram

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | prod | пусто | Токен бота от @BotFather. `chat_id` — в админке. |

## amoCRM

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `AMOCRM_BASE_URL` | prod | пусто | `https://<поддомен>.amocrm.ru`. |
| `AMOCRM_CLIENT_ID` | prod | пусто | Из карточки интеграции. |
| `AMOCRM_CLIENT_SECRET` | prod | пусто | Из карточки интеграции. |
| `AMOCRM_REDIRECT_URI` | prod | пусто | Из карточки интеграции. |
| `AMOCRM_PIPELINE_ID` | prod | `0` | ID воронки. `0` = первый этап главной воронки. |
| `AMOCRM_STATUS_ID` | prod | `0` | ID этапа. `0` = по умолчанию. |

!!! warning "ID amoCRM должны быть числом"
    `AMOCRM_PIPELINE_ID` и `AMOCRM_STATUS_ID` нельзя оставлять пустыми —
    ставьте `0`, иначе контейнер `web` не стартует.

## Traefik (`deploy/infra/.env`)

Отдельный файл для стека Traefik (только одна переменная).

| Переменная | Окружение | По умолчанию | Описание |
|---|---|---|---|
| `ACME_EMAIL` | prod | — | E-mail для регистрации сертификатов Let's Encrypt. |
| `COMPOSE_PROJECT_NAME` | prod | `infra` | Имя проекта Compose — фиксирует отдельное имя для инфраструктуры Traefik. |
