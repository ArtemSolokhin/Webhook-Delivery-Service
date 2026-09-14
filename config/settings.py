import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")]

# This is a small, intentionally scoped portfolio project: no auth, no
# frontend, so INSTALLED_APPS / MIDDLEWARE are kept to the minimum Django
# needs to run migrations and serve the Django Ninja API.
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "apps.webhooks",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "webhooks"),
        "USER": os.environ.get("POSTGRES_USER", "webhooks"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "webhooks"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Celery -----------------------------------------------------------
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# Task routing/behaviour is intentionally simple: no periodic tasks (no
# celery beat), no custom queues - a single default queue is enough here.

# --- Webhook delivery ---------------------------------------------------
# How long to wait for a subscriber to respond before treating the
# attempt as failed.
WEBHOOK_TIMEOUT_SECONDS = float(os.environ.get("WEBHOOK_TIMEOUT_SECONDS", "5"))
# Number of *retries* after the first attempt (so up to 1 + this many
# total attempts per event/endpoint pair).
WEBHOOK_MAX_RETRIES = int(os.environ.get("WEBHOOK_MAX_RETRIES", "3"))
# Delay (seconds) before retry #1, #2, #3, applied via Celery's countdown.
WEBHOOK_RETRY_DELAYS_SECONDS = [10, 60, 300]
