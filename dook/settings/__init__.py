import os
import pathlib
import sys

from corsheaders.defaults import default_headers
from envparse import env

from dook.settings.auth import *  # noqa
from dook.settings.email import *  # noqa
from dook.settings.storage import *  # noqa

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


env.read_envfile()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="secret_key")

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = env("DEBUG", default="yes", cast=bool)

# ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["localhost"], cast=list)
ALLOWED_HOSTS = ["*"]


# Application definition
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "dook.core.events",
    "dook.core.news",
    "dook.core.processor",
    "dook.core.users",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dook.api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "templates/auth"),
            os.path.join(BASE_DIR, "templates/news"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dook.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": env(
            "DATABASE_BACKEND", default="django.db.backends.postgresql_psycopg2"
        ),
        "NAME": env("POSTGRES_DB", default="postgres"),
        "HOST": env("POSTGRES_HOST", default="db"),
        "USER": env("POSTGRES_USER", default="postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="postgres"),
        "ATOMIC_REQUESTS": True,
    },
    "readonly": {
        "ENGINE": env(
            "DATABASE_BACKEND", default="django.db.backends.postgresql_psycopg2"
        ),
        "NAME": env("POSTGRES_DB", default="postgres"),
        "HOST": env("POSTGRES_READONLY_HOST", default="db"),
        "USER": env("POSTGRES_USER", default="postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="postgres"),
        "TEST": {"MIRROR": "default",},
    },
}

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "dook.api.paginations.CustomPageNumberPagination",
    "PAGE_SIZE": 20,
}

ATOMIC_REQUESTS = True

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

PUBLIC_ROOT = pathlib.Path(BASE_DIR, "public")

MEDIA_ROOT = env("MEDIA_ROOT", default=str(pathlib.Path(PUBLIC_ROOT, "media")) + "/")
STATIC_ROOT = env("STATIC_ROOT", default=str(pathlib.Path(PUBLIC_ROOT, "static")) + "/")

MEDIA_URL = env("MEDIA_URL", default=str(pathlib.Path(PUBLIC_ROOT, "media")) + "/")
STATIC_URL = env("STATIC_URL", default=str(pathlib.Path(PUBLIC_ROOT, "static")) + "/")

CORS_ORIGIN_ALLOW_ALL = env("CORS_ORIGIN_ALLOW_ALL", default=False, cast=bool)
CORS_ALLOW_HEADERS = list(default_headers) + ["Cache-Control", "Pragma"]

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")

# fmt: off
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple',
        }
    },
    'formatters': {
        'verbose': {
            'format': '[{levelname} {asctime}] {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt':'%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname} {asctime}] {message}',
            'style': '{',
            'datefmt':'%Y-%m-%d %H:%M:%S',
        },
    },
    "loggers": {
        "processor": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "events": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
}
# fmt: on

INVITATION_EXPIRY = 7
ASSIGNMENT_ACTIVITY_PERIOD_MINUTES = 5  # minutes
TARGET_ASSIGNMENTS_PER_NEWS_COUNT = 4

PANEL_DOMAIN_NAME = env("DOMAIN_NAME", default="panel.app.fakehunter.pap.pl")

# TODO: Add subscribers autodiscovery
EVENTS = {
    "news_new_verdict": [
        "dook.core.integrations.chatbot.events.ChatbotNewsNewVerdictSubscriber",
        "dook.core.users.events.NewsNewVerdictSubscriber",
    ],
    "news_edit_verdict": [
        "dook.core.integrations.chatbot.events.ChatbotNewsEditVerdictSubscriber",
    ],
}

CHATBOT_API_URL = env("CHATBOT_API_URL", default="")
CHATBOT_API_KEY = env("CHATBOT_API_KEY", default="")
