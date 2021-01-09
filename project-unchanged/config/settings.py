import os, datetime
from .utils import get_env
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = get_env("SECRET_KEY")
DEBUG = False
ADMIN_ENABLED = get_env("ADMIN_ENABLED") == "True"
ALLOWED_HOSTS = get_env("ALLOWED_HOSTS").split("|")
CORS_ALLOWED_ORIGINS = get_env("CORS_ORIGIN_WHITELIST").split("|")
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = None
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "users.apps.UsersConfig",
    "authentication.apps.AuthenticationConfig",
    "company.apps.CompanyConfig",
    "django_seed",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("DB_NAME"),
        "HOST": get_env("DB_HOSTNAME"),
        "PORT": get_env("DB_PORT"),
        "USER": get_env("DB_USERNAME"),
        "PASSWORD": get_env("DB_PASSWORD"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated",],
    "DEFAULT_AUTHENTICATION_CLASSES": ["authentication.auth_classes.JWTAuth",],
}

JWT_AUTH = {
    "JWT_SECRET_KEY": get_env("JWT_SECRET"),
    "JWT_EXPIRATION_DELTA": datetime.timedelta(seconds=int(get_env("JWT_EXPIRATION_DELTA"))),
    "JWT_ALLOW_REFRESH": True,
    "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(
        seconds=int(get_env("JWT_REFRESH_EXPIRATION_DELTA"))
    ),
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]
