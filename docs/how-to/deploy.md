# Deploy to a server

How to deploy the project to a server and how to ship updates.
This document is the primary source on deployment.

Live demo of the project: **<https://demoplast.skerter.dev>**.

## How production is built

A single VPS (Selectel VDS, Ubuntu 24.04) running Docker Compose. The project stack
([`deploy/selectel/compose.yaml`](https://github.com/Skerter/django-plastic-landing/blob/main/deploy/selectel/compose.yaml)):

- `web` — Django + gunicorn (runs migrations, `collectstatic` and the demo seed on startup),
- `db` — PostgreSQL 16,
- `media` — nginx, serves `/media/` only (admin uploads).

The entry reverse proxy is a **shared Traefik** on `:80/:443`, which issues and
renews Let's Encrypt TLS certificates itself (resolver `le`). Traefik lives in its
own stack and connects to the project through the external docker network `proxy`;
CI never touches it. More on the design — [Architecture](../explanation/architecture.md).

**Cloudflare** sits in front of the server in proxy mode: the domain's DNS record is
orange, so a visitor connects to a Cloudflare edge node, which in turn reaches the VPS.
This hides the
server IP and adds a CDN. The origin certificate is still issued by Traefik — Cloudflare
does not replace Let's Encrypt, it works on top of it.

The image is built in **GitHub Actions** and pushed to **GHCR**
(`ghcr.io/skerter/django-plastic-landing`); the server only pulls the ready image —
nothing is built on the VPS (avoiding load and OOM).

```
Internet
      │
      ▼
  ┌────────────┐
  │ Cloudflare │  proxied, encryption mode Full
  └────────────┘
      │ :80/:443
      ▼
  ┌──────────┐   docker network "proxy" (external)
  │ Traefik  │◄────────┬──────────────┐
  └──────────┘    ┌─────▼────┐   ┌─────▼──────┐
                  │   web    │   │   media    │
                  │ gunicorn │   │ nginx      │
                  └─────┬────┘   └────────────┘
            network "demoplast_internal" (private)
                  ┌─────▼──────┐
                  │     db     │
                  └────────────┘
```

`web` and `media` are on the `proxy` network (Traefik discovers them by docker labels);
`db` is only on the internal `demoplast_internal`. Static files are served by
WhiteNoise inside `web`; admin uploads (`/media/`) by the `media` service.

---

## First deploy to a new server

Done once by hand: the secrets, the `.env` and the `proxy` docker network do not exist
on the server yet. Subsequent deploys are automatic (see [below](#update-production)).

This assumes the server is already prepared: a `deploy` user with sudo and SSH key
access, an open firewall (22/80/443), Docker + Compose installed, and the shared
Traefik running with the external `proxy` network. Connecting and the basic commands —
[Operations](operations.md).

### 1. Clone the repository

```bash
sudo mkdir -p /opt/django-plastic-landing
sudo chown deploy:deploy /opt/django-plastic-landing
git clone https://github.com/Skerter/django-plastic-landing.git /opt/django-plastic-landing
cd /opt/django-plastic-landing
```

### 2. Log in to the image registry (GHCR)

```bash
echo "<GHCR_TOKEN>" | docker login ghcr.io -u <github-user> --password-stdin
```

`GHCR_TOKEN` is a Personal Access Token (classic) with the `read:packages` scope
(GitHub → Settings → Developer settings → Tokens (classic)).

### 3. Create the project `.env`

```bash
cp deploy/selectel/.env.example deploy/selectel/.env
nano deploy/selectel/.env
```

The `.env` sits **next to** `compose.yaml` — Compose reads it both for `${...}`
interpolation and as the containers' `env_file:`. Fill in at least:

- `SECRET_KEY` — `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `POSTGRES_PASSWORD` — a strong password; **the same one** in `DATABASE_URL`
- `ALLOWED_HOSTS` and `SITE_DOMAIN` — the site domain
- `DJANGO_SETTINGS_MODULE=config.settings.prod`, `DEBUG=False`

The full list of variables — [Environment variables](../reference/environment.md).
Notification channels (SMTP/Telegram) can be filled in later —
[Notification channels](enable-notification-channels.md).

### 4. Make sure the external docker network exists

```bash
docker network create proxy   # if the shared Traefik stack has not created it yet
```

The `proxy` network (`external: true`) is shared with Traefik. Without it the
project's `up -d` fails.

### 5. Bring the project up

```bash
docker compose -f deploy/selectel/compose.yaml pull
docker compose -f deploy/selectel/compose.yaml up -d
```

On startup `web` runs the migrations, the demo seed and `collectstatic` itself. For the
domain from `SITE_DOMAIN`, Traefik automatically requests a production Let's Encrypt
certificate — as soon as the site is up, the browser shows a valid padlock.

!!! warning "Production Let's Encrypt rate limit"
    5 certificates per week per domain. Do not recreate the Traefik certificate
    volume without a reason — you may hit the limit.

### 6. Create an administrator

```bash
docker compose -f deploy/selectel/compose.yaml exec web \
  python manage.py createsuperuser
```

Next — [fill the catalog through the admin](add-product-via-admin.md) and
[enable the notification channels](enable-notification-channels.md).

---

## Update production

Deployment is automatic: a push to `main` triggers
[GitHub Actions](https://github.com/Skerter/django-plastic-landing/blob/main/.github/workflows/deploy.yaml),
which builds the image, pushes it to GHCR and updates the containers on the server over SSH.

```bash
git push origin main      # ← triggers the build and the deploy
```

Progress is on the **Actions** tab in GitHub. CI runs `git pull` + `docker
compose pull` + `up -d` for the project; migrations, the demo seed and `collectstatic`
are performed by the `web` container itself on startup.

**Manual deploy** (if CI is unavailable):

```bash
cd /opt/django-plastic-landing
git pull
docker compose -f deploy/selectel/compose.yaml pull
docker compose -f deploy/selectel/compose.yaml up -d
```

---

## Go-live: moving to the production domain

The procedure below was verified while moving the demo from a temporary nip.io address
to `demoplast.skerter.dev`. It works the same way for a client's production domain.

The domain is set by a **single** variable `SITE_DOMAIN`, which Compose interpolates into
the Traefik labels — `compose.yaml` needs no edits.

1. **DNS:** an A record for the domain → the server IP. If the domain is on Cloudflare,
   set the record to **DNS only** (grey cloud) while the certificate is issued — see
   the warning below. Lower the TTL to 300 in advance.
2. **`.env` on the server:** `SITE_DOMAIN=<domain>`, `ALLOWED_HOSTS=<domain>`,
   `CSRF_TRUSTED_ORIGINS=https://<domain>`. For several hosts, list them
   comma-separated (`<domain>,www.<domain>`).
3. **Apply:** `docker compose -f deploy/selectel/compose.yaml up -d`.
   Compose sees the changed labels and recreates `web` and `media`, Traefik
   builds a router for the new `Host` and requests a certificate.
4. **Check:** `curl -sI https://<domain>/` → `HTTP/2 200`. A `400` response with
   `server: gunicorn` means the container does not see the domain in `ALLOWED_HOSTS`
   (a common cause is a duplicate variable in `.env` — the last line wins).
5. **Turn the Cloudflare proxy back on** (orange cloud) if you disabled it in step 1,
   and confirm the site still returns `200`.
6. **Open up indexing** in `robots_txt` ([`apps/pages/views.py`](https://github.com/Skerter/django-plastic-landing/blob/main/apps/pages/views.py)):
   the demo uses `Disallow: /`, a production site needs `Allow: /`.

!!! warning "Cloudflare: certificate first, proxy second"
    In `Full` and `Full (Strict)` modes Cloudflare reaches the origin over HTTPS and
    expects a working certificate there. Until Traefik has issued one you get a
    deadlock, and the visitor sees **526 Invalid SSL certificate**. That is why the
    record is switched to DNS only first, the certificate is issued directly, and only
    then the proxy is enabled. The proxy does not interfere with renewals afterwards:
    Cloudflare does not redirect the `/.well-known/acme-challenge/` path.

!!! danger "Flexible mode is incompatible with the project"
    In `Flexible` mode Cloudflare reaches the origin over HTTP, while `SECURE_SSL_REDIRECT`
    in [`config/settings/prod.py`](https://github.com/Skerter/django-plastic-landing/blob/main/config/settings/prod.py)
    sends it back to HTTPS — an infinite redirect loop.
    Only `Full` and `Full (Strict)` are acceptable.
