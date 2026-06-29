# Эксплуатация

Повседневные операции с сервером: подключение, обновление, логи,
резервное копирование, диагностика. Этот документ — основной источник по
эксплуатации.

Все docker-команды выполняются **на сервере** под пользователем `deploy`
из каталога `/opt/django-plastic-landing`.

## Базовые факты о сервере

| Параметр | Значение |
|---|---|
| Хостинг | Selectel VDS, Ubuntu 24.04 |
| SSH-пользователь | `deploy` |
| Каталог проекта | `/opt/django-plastic-landing` |
| Compose проекта | `deploy/selectel/compose.yaml` |
| Reverse-proxy | общий Traefik (внешняя сеть `proxy`) |
| Образ | `ghcr.io/skerter/django-plastic-landing:latest` |
| Демо | <https://demo.135.106.161.48.nip.io> |

!!! note "Traefik — отдельный стек"
    Входной Traefik (точка входа :80/:443 + TLS) живёт сам по себе и подключается
    к проекту через внешнюю docker-сеть `proxy`; CI его не трогает. Команды ниже
    используют `-f deploy/selectel/compose.yaml` — см. [алиас](#удобный-алиас).

---

## 1. Подключение по SSH

Подставьте путь к своему приватному ключу и адрес сервера:

```bash
ssh -i <путь-к-ssh-ключу> <ssh-пользователь>@<IP-сервера>
cd /opt/django-plastic-landing
```

Выйти — `exit` или `Ctrl+D`.

!!! note "Windows"
    В PowerShell домашний каталог — `$env:USERPROFILE` (например
    `"$env:USERPROFILE\.ssh\id_ed25519"`). Если SSH ругается на права доступа
    к ключу, ограничьте их только своим пользователем.

## 2. Реестр образов (GHCR)

Нужен, чтобы тянуть образ. Вход через stdin — токен не светится в истории:

```bash
echo "<GHCR_TOKEN>" | docker login ghcr.io -u <github-пользователь> --password-stdin
```

Токен: GitHub → Settings → Developer settings → Tokens (classic) с правом
`read:packages`. Он же лежит в GitHub-секрете `GHCR_TOKEN` (его использует CI) —
при смене обновить **и** секрет, **и** `docker login` на сервере.

## 3. Редактирование `.env`

`.env` проекта лежит рядом с примером (`deploy/selectel/.env.example`), сам не в git:

- `/opt/django-plastic-landing/deploy/selectel/.env`

```bash
nano deploy/selectel/.env
```

Сохранить в nano: **Ctrl+O** → Enter → **Ctrl+X**. Применить (контейнеры читают
`.env` только при старте):

```bash
docker compose -f deploy/selectel/compose.yaml up -d
```

Полный список переменных — [Переменные окружения](../reference/environment.md).

!!! tip "Что в админке, а что в `.env`"
    Частая путаница. Токены и SMTP — в `.env`; получатель уведомлений,
    Telegram chat_id, ID Метрики — **в админке** (SiteSettings). Таблица
    «где что» — в [Каналах уведомлений](enable-notification-channels.md).

## 4. Контейнеры (docker compose)

**Статус:**
```bash
docker compose -f deploy/selectel/compose.yaml ps
```

**Поднять/обновить стек:**
```bash
docker compose -f deploy/selectel/compose.yaml up -d
```

**Перезапустить один сервис:**
```bash
docker compose -f deploy/selectel/compose.yaml restart web
docker compose -f deploy/selectel/compose.yaml restart media
```

**Пересоздать с нуля** (если закешировал старое состояние):
```bash
docker compose -f deploy/selectel/compose.yaml up -d --force-recreate web
```

**Django management внутри `web`:**
```bash
docker compose -f deploy/selectel/compose.yaml exec web python manage.py <команда>
# напр.: createsuperuser, migrate, shell
```

## 5. Логи

```bash
docker compose -f deploy/selectel/compose.yaml logs web --tail 40
docker compose -f deploy/selectel/compose.yaml logs -f web        # в реальном времени
docker compose -f deploy/selectel/compose.yaml logs media --tail 40
```

Грепы для диагностики:
```bash
docker compose -f deploy/selectel/compose.yaml logs web | grep -i error
```

Логи Traefik (серты, маршруты, ACME) смотрятся в его собственном стеке.

## 6. База данных

**Бэкап в файл:**
```bash
docker compose -f deploy/selectel/compose.yaml exec db \
  pg_dump -U demoplast demoplast > backup_$(date +%F).sql
```

**Восстановить из бэкапа:**
```bash
cat backup_2026-06-19.sql | docker compose -f deploy/selectel/compose.yaml exec -T db \
  psql -U demoplast demoplast
```

**Зайти в psql:**
```bash
docker compose -f deploy/selectel/compose.yaml exec db psql -U demoplast demoplast
```
(выйти — `\q`)

## 7. HTTPS / сертификат

TLS полностью на Traefik (Let's Encrypt, HTTP-01) — никакого certbot. Боевой
сертификат запрашивается автоматически при первом запуске для домена из
`SITE_DOMAIN` (resolver `le`); дальше Traefik сам его продлевает.

!!! warning "Лимит боевого Let's Encrypt"
    5 сертификатов в неделю на домен. Не удаляйте том сертификатов Traefik
    без нужды — пересоздание серта расходует лимит.

## 8. Деплой кода

Автоматический — push в `main`, GitHub Actions собирает образ и обновляет сервер.

Подробнее: [Деплой → обновить прод](deploy.md#обновить-прод).

## 9. Диагностика «сайт не открывается»

1. **Статус контейнеров** — все ли `Up`:
   ```bash
   docker compose -f deploy/selectel/compose.yaml ps
   ```
2. **502 / Bad Gateway** → Traefik не достучался до `web`. Проверь, что `web`
   `Up` и в сети `proxy`; смотри логи Traefik.
3. **`web` рестартится** → смотри его лог (§5), ищи traceback. Обычно причина —
   ошибка в `.env` (см. [Переменные окружения](../reference/environment.md)).
4. **Сертификат не выдаётся** → проверь, что `SITE_DOMAIN` резолвится в IP
   сервера и открыт :80 (HTTP-01 идёт по :80); смотри ACME-логи Traefik.
5. **`/media/` не отдаётся (404)** → проверь сервис `media` и что том
   `media_volume` смонтирован.
6. **Сайт не грузится вообще** → порты снаружи + firewall (`sudo ufw status`),
   Traefik занял :80/:443 (`sudo ss -tlnp | grep -E ':80|:443'`).

## Удобный алиас

Чтобы не писать `-f deploy/selectel/compose.yaml` каждый раз:

```bash
echo "alias dc='docker compose -f /opt/django-plastic-landing/deploy/selectel/compose.yaml'" >> ~/.bashrc
source ~/.bashrc
```

После этого: `dc ps`, `dc logs web --tail 40`, `dc restart web`.
