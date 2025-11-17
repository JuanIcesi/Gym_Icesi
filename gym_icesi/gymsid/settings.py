"""
Django settings for gymsid project.
Generado por 'django-admin startproject' (Django 5.2.8)
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# ----------------------------------------------------
# Rutas base
# ----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------
# Carga de variables desde el archivo .env
# ----------------------------------------------------
load_dotenv(BASE_DIR / ".env")

# ----------------------------------------------------
# Seguridad
# ----------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key")
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)

# ----------------------------------------------------
# Aplicaciones instaladas
# ----------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "fit",
]

# ----------------------------------------------------
# Middleware
# ----------------------------------------------------
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

ROOT_URLCONF = "gymsid.urls"

# ----------------------------------------------------
# Templates
# ----------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "fit.context_processors.nav_trainers",
            ],
        },
    }
]

WSGI_APPLICATION = "gymsid.wsgi.application"

# ----------------------------------------------------
# Base de datos (config desde .env)
# ----------------------------------------------------
DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.postgresql")
DB_CONFIG = {
    "ENGINE": DB_ENGINE,
    "NAME": os.getenv("DB_NAME", "neondb"),
}

# Solo agregar configuraciones adicionales si no es SQLite
if "sqlite" not in DB_ENGINE:
    DB_CONFIG.update({
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "options": "-c client_encoding=UTF8",
        },
    })

DATABASES = {
    "default": DB_CONFIG
}

# ----------------------------------------------------
# Validación de contraseñas
# ----------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------------------------------
# Internacionalización
# ----------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------
# Archivos estáticos
# ----------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ----------------------------------------------------
# Config de login/logout
# ----------------------------------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# ----------------------------------------------------
# Clave primaria por defecto
# ----------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------------------------------
# Backends de autenticación
# ----------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "fit.auth_backend.InstitutionalBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ----------------------------------------------------
# Logging
# ----------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# ----------------------------------------------------
# MongoDB Configuration (NoSQL para datos del gimnasio)
# ----------------------------------------------------
MONGODB_ENABLED = os.getenv("MONGODB_ENABLED", "True") == "True"
MONGODB_SETTINGS = {
    "host": os.getenv("MONGODB_HOST", "clustergym.pxczpdo.mongodb.net"),
    "port": int(os.getenv("MONGODB_PORT", "27017")),
    "db": os.getenv("MONGODB_DB_NAME", "sid_gym_icesi"),
    "username": os.getenv("MONGODB_USERNAME", "gym_user"),
    "password": os.getenv("MONGODB_PASSWORD", "EKKLsiwKQjNJkBdu"),
    "authentication_source": os.getenv("MONGODB_AUTH_SOURCE", "admin"),
}
