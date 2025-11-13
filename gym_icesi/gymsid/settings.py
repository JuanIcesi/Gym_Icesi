"""
Django settings for gymsid project.
Generado por 'django-admin startproject' (Django 5.2.8)
"""

from pathlib import Path
import os
from dotenv import load_dotenv  # Para leer variables desde el .env

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
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Configuración CSRF para desarrollo
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000", "http://localhost:8000"]
CSRF_COOKIE_SECURE = False  # False en desarrollo, True en producción con HTTPS
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False  # False en desarrollo, True en producción con HTTPS
SESSION_COOKIE_HTTPONLY = True

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

    # Utilidades extra
    "django.contrib.humanize",

    # App del proyecto
    "fit",
]

# ----------------------------------------------------
# Middleware
# ----------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "fit.context_processors.nav_trainers",  # 👈 nuestro menú dinámico
        ],
    },
}]

WSGI_APPLICATION = "gymsid.wsgi.application"

# ----------------------------------------------------
# Base de datos (config desde .env)
# ----------------------------------------------------
# Si hay DB_NAME configurado, usa PostgreSQL
# Si no, usa SQLite por defecto
DB_NAME = os.getenv("DB_NAME", "")
DB_ENGINE = os.getenv("DB_ENGINE", "")

if DB_NAME and (DB_ENGINE == "django.db.backends.postgresql" or not DB_ENGINE):
    # Configuración PostgreSQL (NeonDB o PostgreSQL local)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "OPTIONS": {
                "options": "-c client_encoding=UTF8",  # fuerza UTF-8
            },
            "CONN_MAX_AGE": 0,
        }
    }
else:
    # Configuración SQLite (por defecto para desarrollo)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
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
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

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
# Configuración MongoDB (NoSQL)
# ----------------------------------------------------
MONGODB_SETTINGS = {
    "host": os.getenv("MONGODB_HOST", "localhost"),
    "port": int(os.getenv("MONGODB_PORT", "27017")),
    "db": os.getenv("MONGODB_DB", "gym_icesi"),
    "username": os.getenv("MONGODB_USER", ""),
    "password": os.getenv("MONGODB_PASSWORD", ""),
    "authentication_source": os.getenv("MONGODB_AUTH_SOURCE", "admin"),
}

# Si no hay configuración de MongoDB, se puede usar sin autenticación (desarrollo local)
MONGODB_ENABLED = os.getenv("MONGODB_ENABLED", "True") == "True"

# ----------------------------------------------------
# Backends de autenticación
# ----------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "fit.auth_backend.InstitutionalBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ----------------------------------------------------
# Logging (útil para depurar autenticación)
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
