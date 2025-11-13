"""
Django settings for gymsid project.
Generado por 'django-admin startproject'
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

# Para desarrollo y despliegue en Render (.onrender.com)
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,.onrender.com"
).split(",")

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
            "fit.context_processors.nav_trainers",
        ],
    },
}]

WSGI_APPLICATION = "gymsid.wsgi.application"

# ----------------------------------------------------
# Base de datos (config desde .env)
# ----------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        # Para desarrollo local podrías dejar sqlite como fallback:
        # "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "NAME": os.getenv("DB_NAME", "neondb"),
        "USER": os.getenv("DB_USER", ""),
        # OJO: usamos DB_PASS para ser consistente con tu .env
        "PASSWORD": os.getenv("DB_PASS", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "options": "-c client_encoding=UTF8",
        },
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

# Carpeta con estáticos de la app (para desarrollo)
STATICFILES_DIRS = [BASE_DIR / "static"]

# Carpeta donde collectstatic los copiará (para producción / Render)
STATIC_ROOT = BASE_DIR / "staticfiles"

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
