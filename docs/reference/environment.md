# Environment variables

A complete reference of the environment variables. Configuration is supplied through the
`.env` file in the project root (read by `django-environ`). This is the **single source
of truth** for the variables — the `.env.example` (local) and
`deploy/selectel/.env.example` (production) templates point here.

!!! danger "Secrets are never committed"
    `.env` is listed in `.gitignore`. The repository only stores the `*.example`
    templates without real values. Never commit a filled-in `.env`.

The **Environment** column shows where a variable is needed:
**dev** — local development, **prod** — the server, **both** — everywhere.

---

## Django

| Variable | Environment | Default | Description |
|---|---|---|---|
| `DJANGO_SETTINGS_MODULE` | both | — | The settings module. Locally `config.settings.dev`, in production `config.settings.prod`. |
| `SECRET_KEY` | both | — (required) | Django's cryptographic key. Generate one for production: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`. |
| `DEBUG` | both | `False` | Debug mode. Locally `True`, in production **strictly** `False`. |
| `ALLOWED_HOSTS` | both | empty | A comma-separated list of hosts. Locally `localhost,127.0.0.1`, in production the site domain. |

## Database

| Variable | Environment | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | prod | — | The Postgres connection URL. The host is the compose service name (`db`), not `localhost`. |

!!! note "Locally the database is SQLite"
    The `dev` settings hard-code SQLite (`db.sqlite3`) and do **not** read
    `DATABASE_URL`. The variable is only needed in production (`prod`).

## Postgres (the `db` container)

Read by Docker Compose in production. The values must match `DATABASE_URL`.

| Variable | Environment | Default | Description |
|---|---|---|---|
| `POSTGRES_DB` | prod | — | The database name (`demoplast`). |
| `POSTGRES_USER` | prod | — | The database user (`demoplast`). |
| `POSTGRES_PASSWORD` | prod | — | The password. The same one as in `DATABASE_URL`. |

## Docker Compose

| Variable | Environment | Default | Description |
|---|---|---|---|
| `COMPOSE_PROJECT_NAME` | prod | folder name | The Compose project name — pins the volume names. For this project, `demo-plast`. |
| `SITE_DOMAIN` | prod | — | The domain for Traefik routing and TLS certificate issuance. On the demo, `demoplast.skerter.dev`. The only place where the domain is set: `compose.yaml` interpolates it into the labels. |

## Sentry (error monitoring)

| Variable | Environment | Default | Description |
|---|---|---|---|
| `SENTRY_DSN` | prod | empty | The project DSN on sentry.io. Empty → Sentry is not activated. |
| `SENTRY_TRACES_SAMPLE_RATE` | prod | `0.2` | The share of performance traces (0.0–1.0). |

!!! note "Personal data is stripped"
    Names, phone numbers and e-mails are removed before anything is sent to Sentry
    (`config/sentry.py`, `before_send`) — a 152-FZ requirement. See
    [152-FZ compliance](../explanation/compliance-152fz.md).

## Email (SMTP)

The sender's access for lead notification emails. The recipient is set **in the admin**
(SiteSettings → "E-mail для уведомлений"), not here.

| Variable | Environment | Default | Description |
|---|---|---|---|
| `DEFAULT_FROM_EMAIL` | both | empty | The sender address. **Must match** `EMAIL_HOST_USER`. |
| `EMAIL_HOST` | prod | empty | The SMTP server (`smtp.example.com`). |
| `EMAIL_PORT` | prod | `465` | The SMTP port (typically 465 for implicit SSL). |
| `EMAIL_HOST_USER` | prod | empty | The SMTP login (the sender mailbox address). |
| `EMAIL_HOST_PASSWORD` | prod | empty | An **app password** (not the regular password). |
| `EMAIL_USE_SSL` | prod | `True` | Implicit SSL (port 465). |
| `EMAIL_USE_TLS` | prod | `False` | STARTTLS (port 587). Mutually exclusive with `EMAIL_USE_SSL`. |

!!! warning "SSL and TLS are mutually exclusive"
    `EMAIL_USE_SSL=True` and `EMAIL_USE_TLS=True` cannot be set at the same time — Django
    refuses to start. For Yandex Mail: SSL=True, TLS=False, port 465.

SMTP is not needed locally: the `dev` settings print emails to the console. Setup
details — [Notification channels](../how-to/enable-notification-channels.md).

## Telegram

| Variable | Environment | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | prod | empty | The bot token from @BotFather. The `chat_id` lives in the admin. |

## amoCRM

| Variable | Environment | Default | Description |
|---|---|---|---|
| `AMOCRM_BASE_URL` | prod | empty | `https://<subdomain>.amocrm.ru`. |
| `AMOCRM_CLIENT_ID` | prod | empty | From the integration card. |
| `AMOCRM_CLIENT_SECRET` | prod | empty | From the integration card. |
| `AMOCRM_REDIRECT_URI` | prod | empty | From the integration card. |
| `AMOCRM_PIPELINE_ID` | prod | `0` | The pipeline ID. `0` = the first stage of the main pipeline. |
| `AMOCRM_STATUS_ID` | prod | `0` | The stage ID. `0` = the default. |

!!! warning "The amoCRM IDs must be numbers"
    `AMOCRM_PIPELINE_ID` and `AMOCRM_STATUS_ID` must not be left empty —
    set `0`, otherwise the `web` container will not start.

## Traefik (`deploy/infra/.env`)

A separate file for the Traefik stack (a single variable).

| Variable | Environment | Default | Description |
|---|---|---|---|
| `ACME_EMAIL` | prod | — | The e-mail used to register Let's Encrypt certificates. |
| `COMPOSE_PROJECT_NAME` | prod | `infra` | The Compose project name — pins a separate name for the Traefik infrastructure. |
