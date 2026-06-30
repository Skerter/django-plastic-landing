from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Письма печатаются в консоль runserver — реальный SMTP в dev не нужен
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# В dev отключаем ratelimit — иначе 5/час мешает тестировать форму.
# На проде (prod.py) лимит остаётся боевым.
RATELIMIT_ENABLE = False

# Тесты и локальный dev гоняют реальный путь уведомлений (email в консоль),
# поэтому демо-режим здесь принудительно выключен независимо от .env.
DEMO_MODE = False
