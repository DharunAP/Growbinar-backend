from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'Authentication',
    'static',
    'Sessions'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# Django project settings.py

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),    # timne for access token to expire
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),      # time for refrewsh token to get expire
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    # "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'http://example.com',
    'https://example.com',
)

Formatters={
    "standard": {
        "format": "{levelname} {asctime:s} {name} {filename} {lineno:d} {message}",
        "style": "{",
    },
}

Handlers = {
    'DEBUG_handler':{
        "formatter": "standard",
        'level':'DEBUG',
        'class': 'logging.FileHandler',
        'filename': "./logs/debugs/debug.log",
        # "backupCount": 5,
        # "maxBytes": 1024 * 1024 * 5,  
    },
    'WARN_handler':{
        "formatter": "standard",
        'level':'WARN',
        'class': 'logging.FileHandler',
        'filename': "./logs/warnings/warnings.log",
        # "backupCount": 5,
        # "maxBytes": 1024 * 1024 * 5,  
    },
    'ERR_handler':{
        "formatter": "standard",
        'level':'ERROR',
        'class': 'logging.FileHandler',
        'filename': "./logs/errors/errors.log",
        # "backupCount": 5,
        # "maxBytes": 1024 * 1024 * 5,  
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':Formatters,
    'handlers':Handlers,
    'loggers': {
        'Authentication': {
            'handlers': ['DEBUG_handler','WARN_handler','ERR_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'profile_details': {
            'handlers': ['DEBUG_handler','WARN_handler','ERR_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'Sessions': {
            'handlers': ['DEBUG_handler','WARN_handler','ERR_handler'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}


ROOT_URLCONF = 'Growbinar_Backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['Authentication'],
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

WSGI_APPLICATION = 'Growbinar_Backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':'GrowbinarDB',
        'USER':'Django',
        'PASSWORD':'django',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'verceldb',
#         'USER': 'default',
#         'PASSWORD': 'pJihmtHYq91v',
#         'HOST': 'ep-summer-poetry-a46p88qe-pooler.us-east-1.aws.neon.tech',
#         'PORT': '5432',  # Default PostgreSQL port is 5432
#         'OPTIONS': {
#             'sslmode': 'require',
#             'connect_timeout': 15,
#         }
#     }
# }


# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'dharunpalanisamy5256@gmail.com'
EMAIL_HOST_PASSWORD = 'gqruvarabwlkddgq'
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, '/media/')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "media/"),
)
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
