<div align="center">

# 🏭 DemoPlast — лендинг производителя с лидогенерацией

**Production-ready сайт-каталог производителя пластиковой тары на Django 5.**
SSR-каталог, формы заявок на HTMX, фоновая интеграция с CRM, требования 152-ФЗ,
Docker → Nginx → CI/CD.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-1.x-3366CC)
![Tailwind](https://img.shields.io/badge/Tailwind-v4-38BDF8?logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

> **Что это.** Обезличенный шаблон лендинга производителя, собранный на основе реального
> коммерческого проекта. Все данные заказчика (название, контакты, реквизиты, домен, адрес
> сервера) заменены на вымышленные — компания **«ДемоПласт»**. Репозиторий показывает
> инженерные решения и архитектуру, не раскрывая клиента. Запускается одной командой и
> поднимается с демо-данными — **без единого реального ключа или секрета**.

---

## 📸 Скриншоты

> Поместите изображения в `docs/screenshots/` и они подставятся ниже.

| Главная | Каталог / карточка товара |
|---|---|
| ![Главная](docs/screenshots/home.png) | ![Карточка товара](docs/screenshots/product.png) |

| Форма заявки (152-ФЗ согласие) | Админка / заявки |
|---|---|
| ![Форма заявки](docs/screenshots/lead-form.png) | ![Админка](docs/screenshots/admin.png) |

---

## 🚀 Запуск одной командой

```bash
cp .env.example .env
docker compose up --build
```

Откройте **http://localhost:8000**. При старте контейнер автоматически:
применяет миграции → собирает Tailwind CSS → наполняет каталог и контакты
(сид-миграции) → создаёт демо-заявки → поднимает dev-сервер.

```bash
# Доступ в админку (опционально):
docker compose exec web python manage.py createsuperuser
# затем http://localhost:8000/admin/
```

> **Демо-режим.** В `.env.example` стоит `DEMO_MODE=True`: внешние интеграции
> (SMTP-почта, Telegram, amoCRM) **не вызываются** — заявка сохраняется в БД, каналы
> только пишут в лог `DEMO_MODE: skipped`. Поэтому демо работает без реальных ключей.
> Для боевого режима — `DEMO_MODE=False` и настоящие креды в `.env`.

---

## 🧱 Стек и обоснование

| Технология | Зачем именно она |
|---|---|
| **Django 5 (монолит)** | Шесть страниц и формы не требуют микросервисов. SSR-рендеринг каталога — ради SEO (поисковики видят готовый HTML). Не SPA. |
| **PostgreSQL 16** | Основное хранилище; заодно ORM-брокер для очереди задач — без отдельного Redis. |
| **HTMX** | Интерактив форм (отправка, ошибки, лимит) без тяжёлого JS-фреймворка. Сервер отдаёт HTML-фрагменты. |
| **Tailwind v4 (CLI/`django-tailwind`)** | Дизайн-система собирается, а не тянется с CDN (CDN в проде — антипаттерн). Standalone-бинарь, без Node. |
| **django-q2** | Фоновые задачи (уведомления, пуш в CRM) на ORM-брокере. Без Redis/Celery-инфраструктуры. |
| **django-solo** | Синглтон `SiteSettings` — контакты и реквизиты правятся в админке без кода. |
| **uv** | Быстрый менеджер зависимостей и venv (`uv.lock` фиксирует сборку). |
| **Docker + Nginx + Gunicorn** | Воспроизводимое окружение; в проде — WhiteNoise для статики, Nginx для медиа, certbot для HTTPS. |
| **Sentry** | Мониторинг ошибок в проде. |

---

## ⚙️ Инженерные решения

Самое интересное в проекте — не верстка, а то, как устроены формы, интеграции и соответствие
закону. Кратко:

### 1. Лид сначала в БД, потом в CRM
Заявка пишется в локальную БД **первой** — это source of truth. Пуш в amoCRM идёт
**после**, асинхронно. Падение CRM или протухший OAuth-токен **не теряет заявку и не ломает
форму**: пользователь всегда получает «спасибо». См. [`apps/leads/views.py`](apps/leads/views.py),
[`apps/leads/tasks.py`](apps/leads/tasks.py).

### 2. Фоновые задачи и устойчивость (django-q2)
Уведомления — **веер из трёх независимых каналов** (email / Telegram / amoCRM). Каждый
изолирован: падение одного не мешает остальным. Ретраи нативным механизмом django-q2
(`retry=300s`, `max_attempts=5`). Каналы включаются флагами в админке — выключенный даже не
ставится в очередь. ORM-брокер живёт в Postgres, отдельный воркер — сервис `qcluster`.
См. [`apps/leads/services/`](apps/leads/services/).

### 3. Соответствие 152-ФЗ
- **Два отдельных документа**: «Политика конфиденциальности» и «Согласие на обработку ПДн»
  (закон запрещает зашивать согласие в политику).
- **Чекбокс согласия не предзаполнен**, валидируется **на бэкенде** — форма не отправится
  без галочки. Факт согласия фиксируется (`consent=True` + timestamp).
- **Локализация данных**: хранение в РФ, только Яндекс.Метрика (Google Analytics запрещён),
  и она **не грузится до cookie-согласия** (решение принимается на сервере в шаблоне).
- **Минимизация**: собираем только имя + телефон (email опционально).

### 4. Безопасность форм
Honeypot-поле + `django-ratelimit` (5 заявок/час с IP, отдаётся честный `429`, который htmx
корректно свапает), CSRF на всех формах, в проде — `SECURE_SSL_REDIRECT`, HSTS,
`SESSION/CSRF_COOKIE_SECURE`.

### 5. Mobile-first
Верстка от мобильного к десктопу через брейкпоинты Tailwind: бургер-меню, адаптивная сетка
каталога 1 → 2 → 3 колонки, тач-зоны ≥ 44px, кликабельные `tel:`-ссылки.

### 6. DEMO_MODE
Один флаг (`apps/leads/tasks.py`) отсекает все внешние вызовы — публичное демо поднимается
без реальных ключей CRM/Telegram/SMTP, при этом весь путь «форма → валидация → лид в БД»
работает по-настоящему.

---

## 🗂️ Структура

```
django-plastic-landing/
├── compose.yaml              # dev: web + db (одна команда поднимает демо)
├── compose.prod.yaml         # prod: + gunicorn, nginx, certbot, qcluster
├── Dockerfile                # одностадийный, Tailwind собирается на build
├── pyproject.toml · uv.lock  # зависимости (uv)
├── .env.example              # шаблон dev-окружения (DEMO_MODE=True)
├── .env.prod.example         # шаблон прод-окружения
├── config/
│   ├── settings/             # base · dev · docker · prod
│   ├── urls.py · wsgi.py
├── apps/
│   ├── catalog/              # Category, Product, ProductSpec, ProductImage
│   ├── leads/                # Lead, формы, services/ (mail · telegram · amocrm), tasks
│   ├── pages/                # статические страницы, Certificate, SEO
│   └── core/                 # SiteSettings (solo), context processor, sitemap, cookies
├── templates/                # base + partials + страницы (Django templates + HTMX)
├── theme/                    # django-tailwind: @theme + компонентная CSS
├── static/                   # css/demoplast.css · js/site.js · js/htmx.min.js · img/
├── nginx/                    # конфиг для прода
├── docs/screenshots/         # сюда положить скриншоты для README
└── tests/                    # pytest: leads, catalog, pages, core (33 теста)
```

---

## 🧪 Тесты

```bash
uv sync --extra dev
uv run pytest tests/ -v
```

Покрыто: валидация лид-формы (включая отказ без согласия 152-ФЗ), сохранение `Lead`,
устойчивость каналов уведомлений, диспетчер задач, сервисы email/Telegram/amoCRM (с моками),
вьюхи каталога, `SiteSettings` и Яндекс.Метрика по cookie-согласию.

---

## ☁️ Прод-инфраструктура

В репозитории — полный прод-стек (обезличенный): `compose.prod.yaml` (Gunicorn + Nginx +
certbot + qcluster-воркер), `Dockerfile`, `entrypoint.sh`, `init-letsencrypt.sh` и
GitHub Actions (`.github/workflows/deploy.yaml`): на push в `main` собирается образ →
пушится в GHCR → деплоится по SSH на VPS. Домены, IP, имена аккаунтов в этих файлах —
плейсхолдеры (`demoplast.example`, `your-org`).

---

## 📄 Лицензия

[MIT](LICENSE).
