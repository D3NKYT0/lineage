import os
import random
import string
from pathlib import Path
from dotenv import load_dotenv
from str2bool import str2bool
from .logger import LOGGING as is_LOGGING
from urllib.parse import urlparse
from django.utils.translation import gettext_lazy as _
from celery.schedules import crontab

# =========================== MAIN CONFIGS ===========================

load_dotenv()  # take environment variables from .env.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Enable/Disable DEBUG Mode
DEBUG = str2bool(os.environ.get('DEBUG'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = ''.join(random.choices(
        string.ascii_letters + string.digits, k=32))

ROOT_URLCONF = "core.urls"
AUTH_USER_MODEL = 'home.User'
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = '/'

# =========================== LOGGER CONFIGS ===========================

LOGGING = is_LOGGING

# =========================== CORS CONFIGS ===========================

ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1', 'http://localhost', 'http://127.0.0.1:6085', 'http://localhost:6085',]
X_FRAME_OPTIONS = "SAMEORIGIN"

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and not DEBUG:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

RENDER_EXTERNAL_FRONTEND = os.environ.get('RENDER_EXTERNAL_FRONTEND')
if RENDER_EXTERNAL_FRONTEND and not DEBUG:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_FRONTEND}')

# =========================== INSTALLED APPS CONFIGS ===========================

INSTALLED_APPS = [

    "admin_volt.apps.AdminVoltConfig",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "serve_files",
    "import_export",
    "corsheaders",
    "django_ckeditor_5",
    "widget_tweaks",
    "po_translate",

    "apps.main.administrator",
    "apps.main.auditor",
    "apps.main.faq",
    "apps.main.home",
    "apps.main.message",
    "apps.main.news",
    "apps.main.notification",
    "apps.main.solicitation",

    "apps.lineage.server",
    "apps.lineage.wallet",
    "apps.lineage.payment",
    "apps.lineage.accountancy",
    "apps.lineage.inventory",
    "apps.lineage.shop",
    "apps.lineage.auction",
]

# =========================== MIDDLEWARE CONFIGS ===========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.main.auditor.middleware.AuditorMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "middlewares.access_apps.LoginRequiredAccess",
    "middlewares.forbidden_redirect_middleware.ForbiddenRedirectMiddleware",
    "middlewares.rate_limit_api_external.RateLimitMiddleware",
]

# =========================== TEMPLATES CONFIGS ===========================

HOME_TEMPLATES = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [HOME_TEMPLATES],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.i18n',
            ],
        },
    },
]

# =========================== DATABASE CONFIGS ===========================

RUNNING_IN_DOCKER = os.getenv('RUNNING_IN_DOCKER', 'false').lower() == 'true'

DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
DB_USERNAME = os.getenv('DB_USERNAME' , None)
DB_PASS     = os.getenv('DB_PASS'     , None)
if not RUNNING_IN_DOCKER:
    DB_HOST = 'localhost'
else:
    DB_HOST     = os.getenv('DB_HOST'     , None)
DB_PORT     = os.getenv('DB_PORT'     , None)
DB_NAME     = os.getenv('DB_NAME'     , None)

if DB_ENGINE and DB_NAME and DB_USERNAME:
    DATABASES = {
      'default': {
        'ENGINE'  : 'django.db.backends.' + DB_ENGINE,
        'NAME'    : DB_NAME,
        'USER'    : DB_USERNAME,
        'PASSWORD': DB_PASS,
        'HOST'    : DB_HOST,
        'PORT'    : int(DB_PORT) if DB_PORT else '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }
    
# =========================== PASSWORD VALIDATION CONFIGS ===========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =========================== INTERNATIONALIZATION CONFIGS ===========================

LANGUAGE_CODE = os.getenv("CONFIG_LANGUAGE_CODE", "pt")
TIME_ZONE = os.getenv("CONFIG_TIME_ZONE", "America/Recife")
USE_I18N = True
USE_L10N = True
USE_TZ = True
DECIMAL_SEPARATOR = os.getenv("CONFIG_DECIMAL_SEPARATOR", ',')
USE_THOUSAND_SEPARATOR = os.getenv("CONFIG_USE_THOUSAND_SEPARATOR", "True").lower() in ['true', '1', 'yes']
DATETIME_FORMAT = os.getenv("CONFIG_DATETIME_FORMAT", 'd/m/Y H:i:s')
DATE_FORMAT = os.getenv("CONFIG_DATE_FORMAT", 'd/m/Y')
TIME_FORMAT = os.getenv("CONFIG_TIME_FORMAT", 'H:i:s')
GMT_OFFSET = float(os.getenv("CONFIG_GMT_OFFSET", -3))

LANGUAGES = [
    ('pt', _('Português')),
    ('en', _('Inglês')),
    ('es', _('Espanhol')),
]

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# =========================== STATIC FILES CONFIGS ===========================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Defina a URL base para os arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# =========================== EMAIL CONFIGS ===========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
CONFIG_EMAIL_ENABLE = os.getenv('CONFIG_EMAIL_ENABLE', False)
if CONFIG_EMAIL_ENABLE:
    EMAIL_USE_TLS = os.getenv('CONFIG_EMAIL_USE_TLS')
    EMAIL_HOST = os.getenv('CONFIG_EMAIL_HOST')
    EMAIL_HOST_USER = os.getenv('CONFIG_EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('CONFIG_EMAIL_HOST_PASSWORD')
    EMAIL_PORT = os.getenv('CONFIG_EMAIL_PORT')
    DEFAULT_FROM_EMAIL = os.getenv('CONFIG_DEFAULT_FROM_EMAIL')

# =========================== CACHES CONFIGS ===========================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache' if not DEBUG else 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': os.getenv('DJANGO_CACHE_REDIS_URI') if not DEBUG else 'unique-snowflake',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_TIMEOUT': 5,  # Ajuste conforme necessário
            'KEY_PREFIX': 'suop',  # Prefixo opcional para suas chaves
        } if not DEBUG else {}
    }
}

# =========================== CELERY CONFIGS ===========================

# e.g., 'redis://localhost:6379/0'
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URI')
# e.g., 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = os.getenv('CELERY_BACKEND_URI')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = False  # Altere para True se não precisar dos resultados
CELERY_TIMEZONE = TIME_ZONE
# Pode ser definido como False se não precisar de rastreio
CELERY_TRACK_STARTED = True

CELERY_BEAT_SCHEDULE = {
    'encerrar-leiloes-expirados-cada-minuto': {
        'task': 'apps.lineage.auction.tasks.encerrar_leiloes_expirados',
        'schedule': crontab(minute='*/1'),
    },
}

# =========================== CHANNELS CONFIGS ===========================

if DEBUG:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

else:
    channels_backend = os.getenv('CHANNELS_BACKEND')
    redis_url = urlparse(channels_backend)
    redis_host = redis_url.hostname
    redis_port = redis_url.port

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(redis_host, redis_port)],
            }
        }
    }

# =========================== SECURITY CONFIG ===========================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# =========================== ENCRYPTION CONFIG ===========================

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    raise ValueError("A variável de ambiente ENCRYPTION_KEY não está definida.")
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 2621440))  # Valor padrão: 2.5 MB
SERVE_DECRYPTED_FILE_URL_BASE = os.environ.get('SERVE_DECRYPTED_FILE_URL_BASE')

# =========================== AUDITOR CONFIGS ===========================

AUDITOR_MIDDLEWARE_ENABLE = os.getenv('CONFIG_AUDITOR_MIDDLEWARE_ENABLE', False)
AUDITOR_MIDDLEWARE_RESTRICT_PATHS = os.getenv('CONFIG_AUDITOR_MIDDLEWARE_RESTRICT_PATHS', [])

# =========================== EXTRA CONFIGS ===========================

customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png'] # optional
CKEDITOR_5_MAX_FILE_SIZE = 5 # Max size in MB
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': ['heading', '|', 'bold', 'italic', 'link',
                      'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
                    }

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': {
            'items': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                      'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',
                    ],
            'shouldNotGroupWhenFull': True
        },
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

# =========================== PAYMENTS CONFIGS ===========================

MERCADO_PAGO_ACCESS_TOKEN = os.getenv(
    'CONFIG_MERCADO_PAGO_ACCESS_TOKEN',
    ""
)

MERCADO_PAGO_PUBLIC_KEY = os.getenv(
    'CONFIG_MERCADO_PAGO_PUBLIC_KEY',
    ""
)

MERCADO_PAGO_CLIENT_ID = os.getenv(
    'CONFIG_MERCADO_PAGO_CLIENT_ID',
    ""
)

MERCADO_PAGO_CLIENT_SECRET = os.getenv(
    'CONFIG_MERCADO_PAGO_CLIENT_SECRET',
    ""
)

MERCADO_PAGO_WEBHOOK_SECRET = os.getenv(
    'CONFIG_MERCADO_PAGO_SIGNATURE',
    ""
)

MERCADO_PAGO_SUCCESS_URL = os.getenv(
    'CONFIG_MERCADO_PAGO_SUCCESS_URL',
    "https://pdl.denky.dev.br/app/payment/mercadopago/sucesso/"
)

MERCADO_PAGO_FAILURE_URL = os.getenv(
    'CONFIG_MERCADO_PAGO_FAILURE_URL',
    "https://pdl.denky.dev.br/app/payment/mercadopago/erro/"
)

# =========================== HCAPTCHA CONFIGS ===========================

HCAPTCHA_SITE_KEY = os.environ.get('CONFIG_HCAPTCHA_SITE_KEY')
HCAPTCHA_SECRET_KEY = os.environ.get('CONFIG_HCAPTCHA_SECRET_KEY')
