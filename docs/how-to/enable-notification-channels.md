# Enable notification channels

For every new lead the site can notify three independent channels:
**Email**, **Telegram**, **amoCRM**. They are enabled separately — one of them,
or all three.

## How it works

1. The lead is **saved to the database first** — this always happens, regardless
   of the channels. The lead is never lost, even if every notification fails.
2. The site then queues tasks only for the **enabled** channels
   (the background worker `qcluster`). The form does not wait for them — the user
   sees the "thank you" immediately.
3. If a channel is only partially configured, it is simply skipped with a log entry;
   the others keep working.

More on the flow — in the [Architecture](../explanation/architecture.md) section.

## Two-level configuration

Every channel needs **two things**:

| Level | Where it is set | What it sets |
|---|---|---|
| **Switch** | Admin → Site settings → "Notifications and analytics" | the "enable channel" checkbox + the recipient (email / chat_id) |
| **Credentials** | The `.env` file on the server | tokens and passwords (never visible on the site) |

The admin checkbox only permits the attempt; without credentials in `.env` the channel
is skipped anyway. This split is deliberate: secrets are not stored in the database
and are not shown in the interface.

After editing `.env` on the server the containers have to be restarted — see
[Operations](operations.md).

---

## Email

**The recommended channel** (enabled by default). An email about the lead is sent
to the configured address.

**In the admin** (Site settings → Notifications and analytics):

- ✅ **Отправлять заявки на email** (send leads by email)
- **E-mail для уведомлений** (notification e-mail) — the recipient address. If empty,
  the channel is skipped.

!!! warning "This is not the sales e-mail"
    "E-mail для уведомлений" (notification e-mail) and "E-mail отдела продаж" (sales
    e-mail) are **different fields**. The first is hidden and only serves lead
    notifications; the second is shown on the "Contacts" page. Do not mix them up.

**In `.env`** (the sender's SMTP access):

```bash
DEFAULT_FROM_EMAIL=noreply@example.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=465
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=<app password>
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
```

Things that matter when configuring SMTP:

- **`EMAIL_HOST_USER` and `DEFAULT_FROM_EMAIL` must match** — mail
  providers do not allow sending on someone else's behalf.
- `EMAIL_HOST_PASSWORD` is usually an **app password**, not the main mailbox
  password (it is created in the mail account's security settings).
- **SSL or TLS, not both.** For port 465 — `EMAIL_USE_SSL=True`,
  `EMAIL_USE_TLS=False`. With both flags `True` Django refuses to start.

The example above is for a typical SMTP provider (port 465, SSL). A full field reference —
[Environment variables](../reference/environment.md).

!!! note "No mail is sent in development"
    Locally (`dev`) emails are printed to the `runserver` console — no real SMTP
    is needed. Actual delivery happens in production only.

---

## Telegram

The notification arrives as a chat message from a bot.

**In the admin:**

- ✅ **Отправлять уведомления в Telegram** (send notifications to Telegram)
- **Telegram chat_id** — the numeric chat ID (not a `@username`).

**In `.env`:**

```bash
TELEGRAM_BOT_TOKEN=<bot token from @BotFather>
```

If the token or the chat_id is empty, the channel is skipped.

!!! warning "Telegram API reachability depends on the server's network"
    Telegram has to be reachable from the server. If the API is unavailable, the channel
    fails gracefully (the lead is still saved and the form answers "thank you"), and a
    network error appears in the `qcluster` logs.

---

## amoCRM

The lead is pushed to the CRM: a contact and a deal are created.

**In the admin:**

- ✅ **Отправлять заявки в amoCRM** (send leads to amoCRM)

**In `.env`:**

```bash
AMOCRM_BASE_URL=https://<subdomain>.amocrm.ru
AMOCRM_CLIENT_ID=<from the integration card>
AMOCRM_CLIENT_SECRET=<from the integration card>
AMOCRM_REDIRECT_URI=<from the integration card>
AMOCRM_PIPELINE_ID=0      # 0 = the first stage of the main pipeline
AMOCRM_STATUS_ID=0
```

!!! warning "Empty IDs break the production start-up"
    `AMOCRM_PIPELINE_ID` and `AMOCRM_STATUS_ID` must be numbers. If you are not choosing
    a pipeline, set `0` instead of leaving them empty, otherwise the `web` container
    will not start.

**One-time authorization.** The integration uses OAuth 2.0 — on top of the credentials it
needs an initial authorization (exchanging the code for tokens). On the server:

```bash
docker compose -f deploy/selectel/compose.prod.yaml exec web \
  python manage.py amocrm_auth <code>
```

`<code>` is the authorization code from the amoCRM integration card. After that the tokens
are stored in the database and refreshed automatically. Without this step the channel
is skipped with a "not authorized" log entry.

---

## Verification

Once configured, submit a test lead through a form on the site and check that:

- the record appeared in the admin (**Заявки**, Leads);
- the notification arrived through the enabled channels;
- if something is wrong — the worker logs:

`docker compose -f deploy/selectel/compose.prod.yaml logs -f qcluster`.

!!! note "`.env` changes apply after a restart"
    Containers read `.env` at startup. After editing variables, restart the
    stack (`up -d`) — see [Operations](operations.md).
