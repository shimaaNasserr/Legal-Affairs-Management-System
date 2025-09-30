import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Secret & Debug
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Allowed hosts
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Auth
AUTH_USER_MODEL = 'accounts.User'

# Cloudinary settings
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# Installed Apps
INSTALLED_APPS = [
    # Django default
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Local apps
    "accounts",

    # REST Framework
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",

    # Auth & Registration
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Third-party
    "corsheaders",
    "cloudinary",
    "cloudinary_storage",
]

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",   
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# URLs & WSGI
ROOT_URLCONF = "legal_affairs_backend.urls"
WSGI_APPLICATION = "legal_affairs_backend.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"

# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Site ID for allauth
SITE_ID = 1
