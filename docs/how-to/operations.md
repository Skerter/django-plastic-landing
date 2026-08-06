# Operations

Day-to-day work with the server: connecting, updating, logs,
backups, diagnostics. This document is the primary source on
operations.

All docker commands are run **on the server** as the `deploy` user
from the `/opt/django-plastic-landing` directory.

## Server facts

| Parameter | Value |
|---|---|
| Hosting | Selectel VDS, Ubuntu 24.04 |
| SSH user | `deploy` |
| Project directory | `/opt/django-plastic-landing` |
| Project Compose file | `deploy/selectel/compose.yaml` |
| Reverse proxy | shared Traefik (external network `proxy`) |
| Image | `ghcr.io/skerter/django-plastic-landing:latest` |
| DNS and CDN | Cloudflare (record proxied) |
| Demo | <https://demoplast.skerter.dev> |

!!! note "Traefik is a separate stack"
    The entry Traefik (the :80/:443 entrypoint + TLS) lives on its own and connects
    to the project through the external docker network `proxy`; CI never touches it.
    The commands below use `-f deploy/selectel/compose.yaml` — see the [alias](#a-handy-alias).

---

## 1. Connecting over SSH

Substitute the path to your private key and the server address:

```bash
ssh -i <path-to-ssh-key> <ssh-user>@<server-IP>
cd /opt/django-plastic-landing
```

To leave — `exit` or `Ctrl+D`.

!!! note "Windows"
    In PowerShell the home directory is `$env:USERPROFILE` (for example
    `"$env:USERPROFILE\.ssh\id_ed25519"`). If SSH complains about the key's
    permissions, restrict them to your user only.

## 2. Image registry (GHCR)

Needed to pull the image. Logging in through stdin keeps the token out of the shell history:

```bash
echo "<GHCR_TOKEN>" | docker login ghcr.io -u <github-user> --password-stdin
```

The token: GitHub → Settings → Developer settings → Tokens (classic) with the
`read:packages` scope. The same token is stored in the `GHCR_TOKEN` GitHub secret
(used by CI) — when rotating it, update **both** the secret **and** the `docker login`
on the server.

## 3. Editing `.env`

The project `.env` sits next to its example (`deploy/selectel/.env.example`) and is not in git:

- `/opt/django-plastic-landing/deploy/selectel/.env`

```bash
nano deploy/selectel/.env
```

Saving in nano: **Ctrl+O** → Enter → **Ctrl+X**. To apply (containers read
`.env` only at startup):

```bash
docker compose -f deploy/selectel/compose.yaml up -d
```

The full list of variables — [Environment variables](../reference/environment.md).

!!! tip "What lives in the admin and what in `.env`"
    A common confusion. Tokens and SMTP go into `.env`; the notification recipient,
    the Telegram chat_id and the Metrica ID go **into the admin** (SiteSettings). The
    "what goes where" table is in [Notification channels](enable-notification-channels.md).

## 4. Containers (docker compose)

**Status:**
```bash
docker compose -f deploy/selectel/compose.yaml ps
```

**Bring up / update the stack:**
```bash
docker compose -f deploy/selectel/compose.yaml up -d
```

**Restart a single service:**
```bash
docker compose -f deploy/selectel/compose.yaml restart web
docker compose -f deploy/selectel/compose.yaml restart media
```

**Recreate from scratch** (if it cached an old state):
```bash
docker compose -f deploy/selectel/compose.yaml up -d --force-recreate web
```

**Django management inside `web`:**
```bash
docker compose -f deploy/selectel/compose.yaml exec web python manage.py <command>
# e.g.: createsuperuser, migrate, shell
```

## 5. Logs

```bash
docker compose -f deploy/selectel/compose.yaml logs web --tail 40
docker compose -f deploy/selectel/compose.yaml logs -f web        # follow in real time
docker compose -f deploy/selectel/compose.yaml logs media --tail 40
```

Greps for diagnostics:
```bash
docker compose -f deploy/selectel/compose.yaml logs web | grep -i error
```

Traefik logs (certificates, routes, ACME) are inspected in its own stack.

## 6. Database

**Back up to a file:**
```bash
docker compose -f deploy/selectel/compose.yaml exec db \
  pg_dump -U demoplast demoplast > backup_$(date +%F).sql
```

**Restore from a backup:**
```bash
cat backup_2026-06-19.sql | docker compose -f deploy/selectel/compose.yaml exec -T db \
  psql -U demoplast demoplast
```

**Open psql:**
```bash
docker compose -f deploy/selectel/compose.yaml exec db psql -U demoplast demoplast
```
(to leave — `\q`)

## 7. HTTPS / certificate

TLS is entirely on Traefik (Let's Encrypt, HTTP-01) — no certbot. The production
certificate is requested automatically on first start for the domain from
`SITE_DOMAIN` (resolver `le`); Traefik renews it on its own afterwards.

Cloudflare sits on top of this: the browser terminates TLS at its edge node, and
Cloudflare opens a separate TLS connection to the origin, where the Traefik certificate
meets it. To check what is actually on the origin, bypass Cloudflare — go by IP and pass
the host name through SNI:

```bash
echo | openssl s_client -connect <server-IP>:443 -servername demoplast.skerter.dev 2>/dev/null \
  | openssl x509 -noout -issuer -subject -dates
```

An `issuer` of `Let's Encrypt` means everything is fine; `CN=TRAEFIK DEFAULT CERT` means
Traefik has no router for that Host and is serving a self-signed placeholder.

!!! warning "Production Let's Encrypt rate limit"
    5 certificates per week per domain. Do not delete the Traefik certificate volume
    without a reason — reissuing a certificate consumes the limit.

!!! note "TODO: switch Cloudflare to Full (Strict)"
    The zone currently runs in **Full** mode: Cloudflare → origin traffic is encrypted,
    but the authenticity of the origin certificate is not verified, so a theoretical MITM
    on that leg remains possible. `demoplast.skerter.dev` already has a valid
    Let's Encrypt certificate, so `Full (Strict)` can be enabled for it without any
    extra preparation.

    The switch is postponed because the encryption mode is set **for the whole zone**
    `skerter.dev` and would affect neighbouring hosts. The careful path is to leave the
    zone alone and add a Configuration Rule with the condition
    `Hostname equals demoplast.skerter.dev` and the setting SSL → `Full (Strict)`.
    Before enabling it, check the certificates of the other proxied hosts with the
    `openssl` command above: any host serving `TRAEFIK DEFAULT CERT` will start
    returning 526 under Strict.

## 8. Deploying code

Automatic — a push to `main`, GitHub Actions builds the image and updates the server.

More detail: [Deploy → update production](deploy.md#update-production).

## 9. Diagnosing "the site does not open"

1. **Container status** — are they all `Up`:
   ```bash
   docker compose -f deploy/selectel/compose.yaml ps
   ```
2. **502 / Bad Gateway** → Traefik could not reach `web`. Check that `web` is
   `Up` and on the `proxy` network; inspect the Traefik logs.
3. **`web` keeps restarting** → read its log (§5), look for a traceback. Usually the cause
   is an error in `.env` (see [Environment variables](../reference/environment.md)).
4. **The certificate is not issued** → check that `SITE_DOMAIN` resolves to the server
   IP and that :80 is open (HTTP-01 goes over :80); inspect the Traefik ACME logs.
   If the domain is proxied by Cloudflare — temporarily switch the record to DNS only,
   issue the certificate directly and turn the proxy back on
   ([Go-live](deploy.md#go-live-moving-to-the-production-domain)).
5. **400 Bad Request with `server: gunicorn`** → Django rejects the `Host`. The domain is
   missing from `ALLOWED_HOSTS`: compare `.env` with what the container actually sees
   (`docker compose -f deploy/selectel/compose.yaml exec web env | grep ALLOWED_HOSTS`) —
   with a duplicate variable in `.env` the last line wins.
6. **526 / 525 from Cloudflare** → the origin has no certificate, or it is invalid for
   the selected encryption mode (see §7).
7. **`/media/` is not served (404)** → check the `media` service and that the
   `media_volume` volume is mounted.
8. **The site does not load at all** → external ports + firewall (`sudo ufw status`),
   Traefik holding :80/:443 (`sudo ss -tlnp | grep -E ':80|:443'`).

## A handy alias

To avoid typing `-f deploy/selectel/compose.yaml` every time:

```bash
echo "alias dc='docker compose -f /opt/django-plastic-landing/deploy/selectel/compose.yaml'" >> ~/.bashrc
source ~/.bashrc
```

After that: `dc ps`, `dc logs web --tail 40`, `dc restart web`.
