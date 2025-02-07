from .base import *

DEBUG = False
env.read_env(BASE_DIR / "config/.env.prod")

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="db"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "DEFAULT_API_URL": "https://hakunamatatarot.com",  # HTTPS URL로 명시
}
