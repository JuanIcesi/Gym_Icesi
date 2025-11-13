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

# Hosts permitidos
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# En Render suelen setear RENDER_EXTERNAL_HOSTNAME
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
    # WhiteNoise para servir estáticos en producción (Render)
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
            "fit.context_processors.nav_trainers",  # menú dinámico de entrenadores
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
        "NAME": os.getenv("DB_NAME", "neondb"),
        "USER": os.getenv("DB_USER", ""),
        # usamos DB_PASS para ser consistente con tu .env local y en Render
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
# URL pública de los estáticos
STATIC_URL = "/static/"

# Carpeta donde collectstatic deja todo (Render lee de aquí)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Carpeta donde tú tienes tus archivos en desarrollo
STATICFILES_DIRS = [BASE_DIR / "static"]

# Almacenamiento de estáticos (Django 4.2+ + WhiteNoise)
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
