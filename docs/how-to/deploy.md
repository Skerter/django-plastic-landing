# Деплой на сервер

Как развернуть проект на сервере и как выкатывать обновления.
Этот документ — основной источник по деплою.

Живое демо проекта: **<https://demo.135.106.161.48.nip.io>**.

## Как устроен прод

Один VPS (Selectel VDS, Ubuntu 24.04), Docker Compose. Стек проекта
([`deploy/selectel/compose.yaml`](https://github.com/Skerter/django-plastic-landing/blob/main/deploy/selectel/compose.yaml)):

- `web` — Django + gunicorn (внутри прогоняет миграции, `collectstatic` и demo-seed),
- `db` — PostgreSQL 16,
- `media` — nginx, отдаёт только `/media/` (загрузки админки).

Входной reverse-proxy — **общий Traefik** на `:80/:443`, который сам выдаёт и
продлевает TLS-сертификаты Let's Encrypt (resolver `le`). Traefik живёт отдельным
стеком и подключается к проекту через внешнюю docker-сеть `proxy`; CI его не
трогает. Подробнее об устройстве — [Архитектура](../explanation/architecture.md).

Образ собирается в **GitHub Actions** и пушится в **GHCR**
(`ghcr.io/skerter/django-plastic-landing`); сервер только тянет готовый образ —
на VPS ничего не собирается (избегаем нагрузки/OOM).

```
Internet :80/:443
      │
      ▼
  ┌──────────┐   docker network "proxy" (external)
  │ Traefik  │◄────────┬──────────────┐
  └──────────┘    ┌─────▼────┐   ┌─────▼──────┐
                  │   web    │   │   media    │
                  │ gunicorn │   │ nginx      │
                  └─────┬────┘   └────────────┘
            network "demoplast_internal" (приватная)
                  ┌─────▼──────┐
                  │     db     │
                  └────────────┘
```

`web` и `media` — в сети `proxy` (их видит Traefik по docker-labels);
`db` — только во внутренней `demoplast_internal`. Статика —
WhiteNoise внутри `web`; загрузки админки (`/media/`) — сервис `media`.

---

## Первый деплой на новый сервер

Делается один раз вручную: секретов, `.env` и docker-сети `proxy` на сервере
ещё нет. Дальнейшие деплои — автоматические (см. [ниже](#обновить-прод)).

Предполагается, что сервер уже подготовлен: пользователь `deploy` с sudo и
доступом по SSH-ключу, открыт firewall (22/80/443), установлен Docker + Compose,
поднят общий Traefik с внешней сетью `proxy`. Подключение и базовые команды —
[Эксплуатация](operations.md).

### 1. Клонировать репозиторий

```bash
sudo mkdir -p /opt/django-plastic-landing
sudo chown deploy:deploy /opt/django-plastic-landing
git clone https://github.com/Skerter/django-plastic-landing.git /opt/django-plastic-landing
cd /opt/django-plastic-landing
```

### 2. Войти в реестр образов (GHCR)

```bash
echo "<GHCR_TOKEN>" | docker login ghcr.io -u <github-пользователь> --password-stdin
```

`GHCR_TOKEN` — Personal Access Token (classic) с правом `read:packages`
(GitHub → Settings → Developer settings → Tokens (classic)).

### 3. Создать `.env` проекта

```bash
cp deploy/selectel/.env.example deploy/selectel/.env
nano deploy/selectel/.env
```

`.env` лежит **рядом с** `compose.yaml` — Compose читает его и для интерполяции
`${...}`, и как `env_file:` контейнеров. Заполнить минимум:

- `SECRET_KEY` — `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `POSTGRES_PASSWORD` — сильный пароль; **тот же** в `DATABASE_URL`
- `ALLOWED_HOSTS` и `SITE_DOMAIN` — домен сайта
- `DJANGO_SETTINGS_MODULE=config.settings.prod`, `DEBUG=False`

Полный список переменных — [Переменные окружения](../reference/environment.md).
Каналы уведомлений (SMTP/Telegram) можно заполнить позже —
[Каналы уведомлений](enable-notification-channels.md).

### 4. Убедиться, что есть внешняя docker-сеть

```bash
docker network create proxy   # если ещё не создана общим Traefik-стеком
```

Сеть `proxy` (`external: true`) общая с Traefik. Без неё `up -d` проекта упадёт.

### 5. Поднять проект

```bash
docker compose -f deploy/selectel/compose.yaml pull
docker compose -f deploy/selectel/compose.yaml up -d
```

`web` при старте сам прогонит миграции, demo-seed и `collectstatic`. Traefik по
домену из `SITE_DOMAIN` автоматически запросит боевой сертификат Let's Encrypt —
как только сайт поднимется, в браузере будет валидный замок.

!!! warning "Лимит боевого Let's Encrypt"
    5 сертификатов в неделю на домен. Не пересоздавайте том сертификатов
    Traefik без нужды — иначе можно упереться в лимит.

### 6. Создать администратора

```bash
docker compose -f deploy/selectel/compose.yaml exec web \
  python manage.py createsuperuser
```

Дальше — [наполнить каталог через админку](add-product-via-admin.md) и
[включить каналы уведомлений](enable-notification-channels.md).

---

## Обновить прод

Деплой автоматический: push в `main` запускает
[GitHub Actions](https://github.com/Skerter/django-plastic-landing/blob/main/.github/workflows/deploy.yaml),
который собирает образ, пушит в GHCR и по SSH обновляет контейнеры на сервере.

```bash
git push origin main      # ← запускает сборку и деплой
```

Прогресс — на вкладке **Actions** в GitHub. CI делает `git pull` + `docker
compose pull` + `up -d` проекта; миграции, demo-seed и `collectstatic` выполняет
сам контейнер `web` при старте.

**Ручной деплой** (если CI недоступен):

```bash
cd /opt/django-plastic-landing
git pull
docker compose -f deploy/selectel/compose.yaml pull
docker compose -f deploy/selectel/compose.yaml up -d
```

---

## Go-live: переезд на боевой домен

Когда понадобится заменить демо-адрес на собственный домен:

1. **DNS** (в панели регистратора домена): A-записи `@` и `www` →
   IP сервера. Заранее снизить TTL до 300.
2. **`.env`:** `ALLOWED_HOSTS=<домен>,www.<домен>`, `SITE_DOMAIN=<домен>`,
   `CSRF_TRUSTED_ORIGINS=https://<домен>`. Traefik по новому `SITE_DOMAIN` сам
   запросит сертификат на боевой домен — `compose.yaml` править не нужно.
3. Перезапустить: `docker compose -f deploy/selectel/compose.yaml up -d`.
4. Снять `noindex`, если стоял для демо, чтобы сайт индексировался.
