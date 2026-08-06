from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Demo mode: when True the external integrations (SMTP email, Telegram, amoCRM) are
# never called — the lead is written to the database and the channels only log
# "demo, skipped". Lets a public demo run without real keys. See apps/leads/tasks.py.
DEMO_MODE = env.bool("DEMO_MODE", default=False)

TAILWIND_APP_NAME = "theme"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django_q",
    "solo",
    "apps.pages",
    "apps.catalog",
    "apps.leads",
    "apps.core",
    "tailwind",
    "theme",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

Q_CLUSTER = {
    "name": "demoplast",
    "workers": 2,
    "timeout": 60,
    "retry": 300,  # wait 5 min for an ack, then hand the task to a worker again (must be > timeout)
    "max_attempts": 5,
    "ack_failures": False,
    "sync": True,  # inline in dev/tests, False in production
    "orm": "default",
}

# Default sender: send_mail() falls back to it when from_email is not passed.
# TODO: set a standard address in .env
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="")
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")

AMOCRM_BASE_URL = env("AMOCRM_BASE_URL", default="")
AMOCRM_CLIENT_ID = env("AMOCRM_CLIENT_ID", default="")
AMOCRM_CLIENT_SECRET = env("AMOCRM_CLIENT_SECRET", default="")
AMOCRM_REDIRECT_URI = env("AMOCRM_REDIRECT_URI", default="")
# int(), but an empty string in .env (AMOCRM_PIPELINE_ID=) counts as "not set".
AMOCRM_PIPELINE_ID = int(env("AMOCRM_PIPELINE_ID", default="") or 0)
AMOCRM_STATUS_ID = int(env("AMOCRM_STATUS_ID", default="") or 0)
