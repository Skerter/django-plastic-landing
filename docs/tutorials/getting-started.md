# Run the project locally

This tutorial takes you from a fresh clone of the repository to a working site
in your browser. Just follow the steps in order — at the end you will see the
home page at `http://127.0.0.1:8000`.

For local development the project uses SQLite (the `db.sqlite3` file), so a
separate database and Docker are **not needed** — everything works out of the box.

## Prerequisites

- Python 3.12 or 3.13
- [uv](https://docs.astral.sh/uv/) — dependency and virtual environment manager
- Git

## Step 1. Clone the repository

```bash
git clone https://github.com/Skerter/django-plastic-landing.git
cd django-plastic-landing
```

## Step 2. Install the dependencies

```bash
uv sync --extra dev
```

The command creates the `.venv` virtual environment and installs Django together
with the dev tools (pytest, playwright).

## Step 3. Create the `.env` file

Copy the template:

```bash
cp .env.example .env
```

Open `.env` and replace `SECRET_KEY=change-me` with any random string — that is
enough for a local run. The remaining values (SMTP, Telegram, amoCRM) are only
needed in production and can be left alone locally.

!!! important "Why the commands below omit `DJANGO_SETTINGS_MODULE`"
    If you run `manage.py` **without** `.env` (or outside `uv run`), Django will
    pick the non-existent `config.settings` module and fail. In that case pass
    the settings explicitly:
    ```bash
    DJANGO_SETTINGS_MODULE=config.settings.dev uv run python manage.py <command>
    ```

    A full description of every variable is in the
    [Environment variables](../reference/environment.md) reference.

## Step 4. Apply the migrations

```bash
uv run python manage.py migrate
```

The command creates the `db.sqlite3` file with all the tables.

## Step 5. Create an administrator

```bash
uv run python manage.py createsuperuser
```

The account is needed to sign in to the `/admin/` panel and fill the catalog.

## Step 6. Build the CSS (Tailwind)

```bash
uv run python manage.py tailwind build
```

Without this step the pages open unstyled. After editing templates the CSS is
rebuilt with the same command (or keep `tailwind start` running — watch mode).

## Step 7. Start the server

```bash
uv run python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and you will see the home
page. The admin panel is at
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## What next

- The catalog is empty — [fill it through the admin](../how-to/add-product-via-admin.md).
- To understand how it all works inside, read the
  [project architecture](../explanation/architecture.md).
