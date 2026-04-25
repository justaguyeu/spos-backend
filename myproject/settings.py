# from datetime import timedelta
# import os
# import dj_database_url
# from pathlib import Path
# from django.core.management.utils import get_random_secret_key

# # import environ 

# # env = environ.Env()
# # environ.Env.read_env()
# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent


# # Quick-start development settings - unsuitable for production
# # See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())

# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,edprintingbackend.onrender.com,edprintingpos.netlify.app/,*').split(',')

# CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', 'http://localhost:3000,https://edprintingpos.netlify.app,https://edprintingbackend.onrender.com').split(',')

# CORS_ALLOW_ALL_ORIGINS = os.getenv('DJANGO_CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'

# CORS_ALLOW_METHODS = [
#     "GET",
#     "POST",
#     "PUT",
#     "DELETE",
#     "OPTIONS",
#     "PATCH",
# ]

# CORS_ALLOW_HEADERS = [
#     "Authorization",
#     "Content-Type",
# ]

# # Application definition

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'myapp',
#     'gunicorn',
#     'corsheaders',
#     'rest_framework',
#     'rest_framework_simplejwt',
# ]

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
#     # ── Pagination: never send 10 000-row responses — cap at 200 rows ──────────
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 200,
#     # ── Throttling: limit abusive clients without blocking real users ─────────
#     'DEFAULT_THROTTLE_CLASSES': [
#         'rest_framework.throttling.AnonRateThrottle',
#         'rest_framework.throttling.UserRateThrottle',
#     ],
#     'DEFAULT_THROTTLE_RATES': {
#         'anon': '60/minute',
#         'user': '300/minute',
#     },
#     # ── Renderer: strip browsable-API overhead in production ──────────────────
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#     ],
# }

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'ROTATE_REFRESH_TOKENS': True,
#     'BLACKLIST_AFTER_ROTATION': True,
# }

# CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', 'http://localhost:3000,https://edprintingpos.netlify.app').split(',')

# MIDDLEWARE = [
#     # WhiteNoise & Security must be FIRST for best performance
#     'django.middleware.security.SecurityMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     'corsheaders.middleware.CorsMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'myproject.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'myproject.wsgi.application'
# # Database
# # https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
#         'NAME': os.getenv('DJANGO_DB_NAME', BASE_DIR / 'db.sqlite3'),
#         'USER': os.getenv('DJANGO_DB_USER', ''),
#         'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
#         'HOST': os.getenv('DJANGO_DB_HOST', ''),
#         'PORT': os.getenv('DJANGO_DB_PORT', ''),
#         # ── Keep DB connections alive for 60 s instead of reconnecting per request
#         'CONN_MAX_AGE': 60,
#         'OPTIONS': {
#             # SQLite: WAL mode allows reads & writes to run concurrently
#             # (ignored by Postgres/MySQL but harmless)
#             'timeout': 20,
#         },
#     }
# }


# # DATABASES = {
# #     'default': {
# #         'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.mysql'),
# #         'NAME': os.getenv('DJANGO_DB_NAME', 'edprinting'),  # Your MySQL database name
# #         'USER': os.getenv('DJANGO_DB_USER', 'root'),   # MySQL database user
# #         'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', 'justaguyeu@gmail.com@1'),  # MySQL password
# #         'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),  # Usually 'localhost' if running locally
# #         'PORT': os.getenv('DJANGO_DB_PORT', '3306'),  # Default MySQL port
# #     }
# # }
# # DATABASES = {
# #     'default': {
# #         'ENGINE': 'django.db.backends.mysql',
# #         'NAME': 'edprinting',
# #         'USER': 'root',
# #         'PASSWORD': 'justaguyeu@gmail.com@1',
# #         'HOST': '127.0.0.1',
# #         'PORT': '3306', 
# #     }
# # }



# # DATABASES = {
# #     'default': {
# #         'ENGINE': 'django.db.backends.postgresql',
# #         'NAME': os.getenv('DB_NAME','edprintingdatabase'),
# #         'USER': os.getenv('DB_USER','edprintingdatabase_user'),
# #         'PASSWORD': os.getenv('DB_PASSWORD','PHqza1el34uTadezLyCJXM42BQJNK4s6'),
# #         'HOST': os.getenv('DB_HOST','dpg-cre2fvrv2p9s73cp8aqg-a'),
# #         'PORT': os.getenv('DB_PORT', '5432'),
# #     }
# # }

# # DATABASES ={
# #     'default': dj_database_url.parse('postgresql://edprintingdatabase_92df_user:WHlyxLF4PD9ROtWu5kT0Vei0mssav1Bf@dpg-d7gd7o1o3t8c73c638ug-a.oregon-postgres.render.com/edprintingdatabase_92df')
# # }


# # TWILIO_ACCOUNT_SID = 'your_account_sid'
# # TWILIO_AUTH_TOKEN = 'your_auth_token'
# # TWILIO_PHONE_NUMBER = '+1234567890'




# # Password validation
# # https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# # Internationalization
# # https://docs.djangoproject.com/en/5.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

# USE_I18N = True

# USE_TZ = True

# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# # Media files (User-uploaded content)
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# # Static file storage using WhiteNoise
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# # Default primary key field type
# # https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # ── Caching — in-memory cache for fast repeated reads ────────────────────────
# # Switch to Redis in production:  'BACKEND': 'django.core.cache.backends.redis.RedisCache'
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'spos-cache',
#         'TIMEOUT': 60,  # default 60 seconds
#     }
# }

# # Logging — WARNING level in production keeps logs lean and fast
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'WARNING' if not DEBUG else 'INFO',
#     },
# }

# # Security settings for production
# if not DEBUG:
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
#     SECURE_BROWSER_XSS_FILTER = True
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     X_FRAME_OPTIONS = 'DENY'
from datetime import timedelta
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# CORE
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,edprintingbackend.onrender.com, https://spos-backend-sdpz.onrender.com",
).split(",")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = os.getenv(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,https://edprintingpos.netlify.app, https://spos-backend-sdpz.onrender.com",
).split(",")

CORS_ALLOW_ALL_ORIGINS = False  # never True in production

CORS_ALLOW_CREDENTIALS = True   # required for httpOnly cookie auth

CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CSRF_TRUSTED_ORIGINS = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost:3000,https://edprintingpos.netlify.app,https://edprintingbackend.onrender.com, https://spos-backend-sdpz.onrender.com",
).split(",")

# ---------------------------------------------------------------------------
# APPS
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "myapp",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",  # needed for refresh rotation
]

# ---------------------------------------------------------------------------
# MIDDLEWARE  (order matters — security & CORS must be first)
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

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

WSGI_APPLICATION = "myproject.wsgi.application"

# ---------------------------------------------------------------------------
# DATABASE  — PostgreSQL via DATABASE_URL env var (set in Render dashboard)
# Falls back to SQLite only for local dev if DATABASE_URL is not set.
# ---------------------------------------------------------------------------
import dj_database_url  # pip install dj-database-url

# _db_default = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

# DATABASES = {
#     "default": dj_database_url.config(
#         default=os.getenv("DATABASE_URL", _db_default),
#         conn_max_age=60,          # keep connections alive 60 s (pool-like)
#         conn_health_checks=True,  # discard stale connections automatically
#     )
# }
DATABASES ={
    'default': dj_database_url.parse('postgresql://sposdatabase_user:HvifBR8DPHkvGzrVCP5zIbQn6rGOVMJC@dpg-d7mdogreo5us73eoj2ug-a.oregon-postgres.render.com/sposdatabase')
}
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
#         'NAME': os.getenv('DJANGO_DB_NAME', BASE_DIR / 'db.sqlite3'),
#         'USER': os.getenv('DJANGO_DB_USER', ''),
#         'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
#         'HOST': os.getenv('DJANGO_DB_HOST', ''),
#         'PORT': os.getenv('DJANGO_DB_PORT', ''),
#         # ── Keep DB connections alive for 60 s instead of reconnecting per request
#         'CONN_MAX_AGE': 60,
#         'OPTIONS': {
#             # SQLite: WAL mode allows reads & writes to run concurrently
#             # (ignored by Postgres/MySQL but harmless)
#             'timeout': 20,
#         },
#     }
# }
# SQLite tuning (only active when using the sqlite fallback locally)
# if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
#     DATABASES["default"].setdefault("OPTIONS", {})["timeout"] = 20

# ---------------------------------------------------------------------------
# CACHE  — Redis via REDIS_URL (Upstash free tier works perfectly)
# Falls back to in-memory for local dev.
# ---------------------------------------------------------------------------
_redis_url = os.getenv("REDIS_URL", "")

if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _redis_url,
            "TIMEOUT": 300,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,   # degrade gracefully if Redis is down
                "SOCKET_CONNECT_TIMEOUT": 3,
                "SOCKET_TIMEOUT": 3,
            },
            "KEY_PREFIX": "spos",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "spos-cache",
            "TIMEOUT": 60,
        }
    }

# ---------------------------------------------------------------------------
# REST FRAMEWORK
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    # Pagination — never send unbounded querysets
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 200,
    # Throttling — company-scoped (see myapp/throttles.py)
    "DEFAULT_THROTTLE_CLASSES": [
        "myapp.throttles.CompanyBurstThrottle",
        "myapp.throttles.CompanySustainedThrottle",
        "myapp.throttles.StrictAnonThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "company_burst":     "60/minute",
        "company_sustained": "1000/hour",
        "strict_anon":       "10/minute",
    },
    # JSON only — strip browsable API in production
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    # Consistent error format
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    # Short access token — if stolen it expires fast
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",

    "TOKEN_OBTAIN_SERIALIZER":  "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
}

# ---------------------------------------------------------------------------
# SECURITY HEADERS
# ---------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = "DENY"
SECURE_REFERRER_POLICY         = "strict-origin-when-cross-origin"

if not DEBUG:
    SECURE_SSL_REDIRECT              = True
    SESSION_COOKIE_SECURE            = True
    CSRF_COOKIE_SECURE               = True
    SECURE_HSTS_SECONDS              = 31536000   # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
    SECURE_HSTS_PRELOAD              = True
    SECURE_PROXY_SSL_HEADER          = ("HTTP_X_FORWARDED_PROTO", "https")

# SECURE_SSL_REDIRECT = False
# ---------------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# INTERNATIONALISATION
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# ---------------------------------------------------------------------------
# STATIC & MEDIA
# ---------------------------------------------------------------------------
STATIC_URL  = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL   = "/media/"
MEDIA_ROOT  = os.path.join(BASE_DIR, "media")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# LOGGING  — lean in production, verbose locally
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING" if not DEBUG else "INFO",
    },
    "loggers": {
        "django.db.backends": {
            "level": "WARNING",   # set to DEBUG locally to see SQL
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

