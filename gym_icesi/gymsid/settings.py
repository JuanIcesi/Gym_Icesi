"""
Django settings for gymsid project.
Generado por 'django-admin startproject' (Django 5.2.8)
"""

from pathlib import Path
import os

# ----------------------------------------------------
# Rutas base
# ----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------
# Seguridad
# ----------------------------------------------------
SECRET_KEY = 'django-insecure-+kw_lt(qq756m89+q%btaga&_59zpbw*1o-z81!$%solzvse+q'
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ----------------------------------------------------
# Aplicaciones instaladas
# ----------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Utilidades extra
    'django.contrib.humanize',

    # App del proyecto
    'fit',
]

# ----------------------------------------------------
# Middleware
# ----------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gymsid.urls'

# ----------------------------------------------------
# Templates
# ----------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 👈 carpeta global
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gymsid.wsgi.application'

# ----------------------------------------------------
# Base de datos (por ahora SQLite)
# ----------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ----------------------------------------------------
# Validación de contraseñas
# ----------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------------------------------
# Internacionalización
# ----------------------------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------
# Archivos estáticos
# ----------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ----------------------------------------------------
# Config de login/logout
# ----------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# ----------------------------------------------------
# Clave primaria por defecto
# ----------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
