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
from django.contrib import messages
from .jazzmin_config import get_jazzmin_settings, get_jazzmin_ui_tweaks
import re

# =========================== MAIN CONFIGS ===========================

load_dotenv()  # take environment variables from .env.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# System Version
VERSION = '1.14.20'

# =========================== THEME CONFIGURATION ===========================

# Control whether to display theme errors to users
# Set to False in production to only log errors without showing them to users
SHOW_THEME_ERRORS_TO_USERS = str2bool(os.environ.get('SHOW_THEME_ERRORS_TO_USERS', True))

# Enable/Disable DEBUG Mode
DEBUG = str2bool(os.environ.get('DEBUG', False))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

ROOT_URLCONF = "core.urls"
AUTH_USER_MODEL = 'home.User'
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = 'dashboard'

# =========================== LOGGER CONFIGS ===========================

LOGGING = is_LOGGING

# Adiciona logging específico para autenticação (versão simplificada)
if 'loggers' not in LOGGING:
    LOGGING['loggers'] = {}

# Loggers de autenticação com handlers seguros
LOGGING['loggers'].update({
    'core.backends': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'apps.main.home.views.accounts': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'apps.main.home.views.commons': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    }
})

# =========================== CORS CONFIGS ===========================

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] if not DEBUG else ['*']

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True  # Permitir todas as origens no desenvolvimento
else:
    CORS_ALLOWED_ORIGINS = ['http://127.0.0.1', 'http://localhost', 'http://127.0.0.1:6085', 'http://localhost:6085',]

CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1', 'http://localhost', 'http://127.0.0.1:6085', 'http://localhost:6085',]
X_FRAME_OPTIONS = "SAMEORIGIN"

def env_to_list(value):
    if not value:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(',') if v.strip()]
    if isinstance(value, list):
        return value
    return [str(value)]

def normalize_origin(host, protocol='https'):
    host = re.sub(r'^https?://', '', host)
    # IPv6: precisa de colchetes
    if ':' in host and not host.startswith('[') and not host.endswith(']'):
        host = f'[{host}]'
    return f'{protocol}://{host}'

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
RENDER_EXTERNAL_FRONTEND = os.environ.get('RENDER_EXTERNAL_FRONTEND')

if not DEBUG:
    # Hostnames
    for host in env_to_list(RENDER_EXTERNAL_HOSTNAME):
        ALLOWED_HOSTS.append(host)
        CORS_ALLOWED_ORIGINS.append(normalize_origin(host))
        CSRF_TRUSTED_ORIGINS.append(normalize_origin(host))
    # Frontends
    for frontend in env_to_list(RENDER_EXTERNAL_FRONTEND):
        ALLOWED_HOSTS.append(frontend)
        CORS_ALLOWED_ORIGINS.append(normalize_origin(frontend))
        CSRF_TRUSTED_ORIGINS.append(normalize_origin(frontend))

# =========================== INSTALLED APPS CONFIGS ===========================

INSTALLED_APPS = [

    'jazzmin',
    "webpack_loader",
    "frontend",

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
    "django_otp",
    "django_otp.plugins.otp_totp",

    "apps.api",

    "apps.main.licence",
    "apps.main.social",
    "apps.main.resources",

    "apps.main.administrator",
    "apps.main.auditor",
    "apps.main.faq",
    "apps.main.home",
    "apps.main.message",
    "apps.main.news",
    "apps.main.notification",
    "apps.main.solicitation",
    "apps.main.downloads",
    "apps.main.calendary",

    "apps.lineage.server",
    "apps.lineage.wallet",
    "apps.lineage.payment",
    "apps.lineage.accountancy",
    "apps.lineage.inventory",
    "apps.lineage.shop",
    "apps.lineage.auction",
    "apps.lineage.games",
    "apps.lineage.reports",
    "apps.lineage.wiki",
    "apps.lineage.roadmap",
    "apps.lineage.tops",

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.discord',

    'django_celery_results',
    'debug_toolbar',
    'django_quill',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'django_api_gen',
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
    "django_otp.middleware.OTPMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # Resource access middleware - deve vir logo após os middlewares básicos do Django
    "apps.main.resources.middleware.ResourceAccessMiddleware",

    'allauth.account.middleware.AccountMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'middlewares.login_attempts.LoginAttemptsMiddleware',
    "middlewares.access_apps.LoginRequiredAccess",
    "middlewares.forbidden_redirect_middleware.ForbiddenRedirectMiddleware",
    "middlewares.rate_limit_api_external.RateLimitMiddleware",
    "middlewares.lock_screen_middleware.SessionLockMiddleware",
    "middlewares.content_filter_middleware.ContentFilterMiddleware",
    "middlewares.content_filter_middleware.SpamProtectionMiddleware",
    
    "apps.main.licence.middleware.LicenseMiddleware",
    "apps.main.licence.middleware.LicenseFeatureMiddleware",
]

# =========================== TEMPLATES CONFIGS ===========================

HOME_TEMPLATES = os.path.join(BASE_DIR, "templates")
THEMES_TEMPLATES = os.path.join(BASE_DIR, "themes")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [HOME_TEMPLATES, THEMES_TEMPLATES],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "core.context_processors.project_metadata",
                "core.context_processors.active_theme",
                "core.context_processors.background_setting",
                "core.context_processors.theme_variables",
                "core.context_processors.slogan_flag",
                "core.context_processors.social_login_config",
                "apps.main.home.context_processors.site_logo",
                "apps.main.home.context_processors.timestamp_processor",
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
    DB_HOST = os.getenv('DB_HOST'     , None)
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
            'OPTIONS': (
                {
                    'connect_timeout': 10,  # OK para PostgreSQL
                } if DB_ENGINE == 'postgresql' else
                {
                    'timeout': 20,
                    'check_same_thread': False,  # OK para SQLite
                } if DB_ENGINE == 'sqlite3' else
                {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    'charset': 'utf8mb4',
                    'autocommit': True,  # OK para MySQL
                }
            )
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,
                'check_same_thread': False,
            }
        }
    }
    
# =========================== PASSWORD VALIDATION CONFIGS ===========================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =========================== AUTHENTICATION BACKENDS CONFIGS ===========================

ACCOUNT_EMAIL_VERIFICATION = os.getenv('ACCOUNT_EMAIL_VERIFICATION', 'none')
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_UNIQUE_EMAIL = True

AUTHENTICATION_BACKENDS = (
    'core.backends.LicenseBackend',  # PRIMEIRO - verifica licença antes de qualquer login
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', default=""),
            'secret': os.getenv('GOOGLE_SECRET_KEY', default=""),
        }
    },
    'github': {
        'APP': {
            'client_id': os.getenv('GITHUB_CLINET_ID', default=""),
            'secret': os.getenv('GITHUB_SECRET_KEY', default=""),
        }
    },
    'discord': {
        'APP': {
            'client_id': os.getenv('DISCORD_CLIENT_ID', default=""),
            'secret': os.getenv('DISCORD_SECRET_KEY', default=""),
        }
    }
}

# =========================== SOCIAL LOGIN CONFIGS ===========================

# Enable/Disable social login globally
SOCIAL_LOGIN_ENABLED = str2bool(os.environ.get('SOCIAL_LOGIN_ENABLED', False))

# Enable/Disable individual providers
SOCIAL_LOGIN_GOOGLE_ENABLED = str2bool(os.environ.get('SOCIAL_LOGIN_GOOGLE_ENABLED', False))
SOCIAL_LOGIN_GITHUB_ENABLED = str2bool(os.environ.get('SOCIAL_LOGIN_GITHUB_ENABLED', False))
SOCIAL_LOGIN_DISCORD_ENABLED = str2bool(os.environ.get('SOCIAL_LOGIN_DISCORD_ENABLED', False))

# Show social login section in templates
SOCIAL_LOGIN_SHOW_SECTION = str2bool(os.environ.get('SOCIAL_LOGIN_SHOW_SECTION', False))

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

# Configuração para exibir data e hora ou apenas data no status dos Grand Bosses
GRANDBOSS_SHOW_TIME = os.getenv("CONFIG_GRANDBOSS_SHOW_TIME", "True").lower() in ['true', '1', 'yes']

# Configuração para exibir quantidade de jogadores online na página inicial
SHOW_PLAYERS_ONLINE = os.getenv("CONFIG_SHOW_PLAYERS_ONLINE", "True").lower() in ['true', '1', 'yes']

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

# =========================== MEDIA PROCESSING CONFIGS ===========================

# Configurações para processamento de mídia (ffmpeg/ffprobe)
FFMPEG_PATH = os.getenv('FFMPEG_PATH', 'ffmpeg')
FFPROBE_PATH = os.getenv('FFPROBE_PATH', 'ffprobe')

# Configurações de upload de arquivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'themes'),
)

# =========================== AWS S3 CONFIGS ===========================

# Configuração para usar S3 da AWS
USE_S3 = os.getenv('USE_S3', 'False').lower() == 'true'

if USE_S3:
    # Configurações do S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    
    # Configurações para arquivos estáticos
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Configurações para arquivos de mídia
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    
    # Configurações adicionais do S3
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'virtual'
    
    # Configurações de segurança (opcional)
    AWS_S3_SECURE_URLS = True
    AWS_S3_VERIFY = True
    
    # Configurações de cache
    AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365  # 1 ano
    
    # Configurações de compressão
    AWS_S3_GZIP = True
    
    # Configurações de CORS (se necessário)
    AWS_S3_CORS_CONFIGURATION = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3000,
            }
        ]
    }

# =========================== EMAIL CONFIGS ===========================

CONFIG_EMAIL_ENABLE = os.getenv('CONFIG_EMAIL_ENABLE', 'False').lower() in ['true', '1', 'yes']
if CONFIG_EMAIL_ENABLE:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    use_tls = os.getenv('CONFIG_EMAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    use_ssl = not use_tls
    EMAIL_HOST = os.getenv('CONFIG_EMAIL_HOST')
    EMAIL_HOST_USER = os.getenv('CONFIG_EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('CONFIG_EMAIL_HOST_PASSWORD')
    # Porta padrão: 587 para TLS, 465 para SSL
    if use_tls:
        EMAIL_USE_TLS = True
        EMAIL_PORT = int(os.getenv('CONFIG_EMAIL_PORT', 587))
    else:
        EMAIL_USE_SSL = True
        EMAIL_PORT = int(os.getenv('CONFIG_EMAIL_PORT', 465))
    DEFAULT_FROM_EMAIL = os.getenv('CONFIG_DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'no-reply@example.com'

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

if DEBUG:
    # Em modo DEBUG, usar configuração que não depende do Redis
    CELERY_TASK_ALWAYS_EAGER = True  # Executa tarefas síncronamente
    CELERY_TASK_EAGER_PROPAGATES = True  # Propaga exceções
    CELERY_BROKER_URL = 'memory://'  # Broker em memória
    CELERY_RESULT_BACKEND = 'cache+memory://'  # Backend em memória
    CELERY_BEAT_SCHEDULE = {}  # Desabilita tarefas periódicas em DEBUG
else:
    # e.g., 'redis://localhost:6379/1'
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URI', 'redis://redis:6379/1')
    # e.g., 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = os.getenv('CELERY_BACKEND_URI', 'redis://redis:6379/1')
    CELERY_BEAT_SCHEDULE = {
        'encerrar-leiloes-expirados-cada-minuto': {
            'task': 'apps.lineage.auction.tasks.encerrar_leiloes_expirados',
            'schedule': crontab(minute='*/1'),
        },
        'encerrar-apoiadores-expirados-cada-minuto': {
            'task': 'apps.lineage.server.tasks.verificar_cupons_expirados',
            'schedule': crontab(minute='*/1'),
        },
    }

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = False  # Altere para True se não precisar dos resultados
CELERY_TIMEZONE = TIME_ZONE
# Pode ser definido como False se não precisar de rastreio
CELERY_TRACK_STARTED = True

# =========================== CHANNELS CONFIGS ===========================

if DEBUG:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

else:
    # e.g., 'redis://localhost:6379/2'
    channels_backend = os.getenv('CHANNELS_BACKEND', 'redis://redis:6379/2')
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
    raise EnvironmentError("The ENCRYPTION_KEY environment variable is not set.")

DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 57671680))
SERVE_DECRYPTED_FILE_URL_BASE = os.environ.get('SERVE_DECRYPTED_FILE_URL_BASE', 'decrypted-file')

# =========================== AUDITOR CONFIGS ===========================

AUDITOR_MIDDLEWARE_ENABLE = os.getenv('CONFIG_AUDITOR_MIDDLEWARE_ENABLE', False)
AUDITOR_MIDDLEWARE_RESTRICT_PATHS = os.getenv('CONFIG_AUDITOR_MIDDLEWARE_RESTRICT_PATHS', [])

# =========================== AUDITOR MIDDLEWARE CONFIGS ===========================

# Configurações do middleware de auditoria
AUDITOR_MIDDLEWARE_ENABLE = str2bool(os.environ.get('CONFIG_AUDITOR_MIDDLEWARE_ENABLE', 'False'))
AUDITOR_MIDDLEWARE_RESTRICT_PATHS = [
    '/static/',
    '/media/',
    '/favicon.ico',
    '/robots.txt',
    '/sitemap.xml',
    '/admin/jsi18n/',
    '/__debug__/',
    '/api/health/',
    '/api/status/',
]
AUDITOR_MIDDLEWARE_MAX_RETRIES = 3
AUDITOR_MIDDLEWARE_RETRY_DELAY = 0.1

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

CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png', 'jpg']
CKEDITOR_5_MAX_FILE_SIZE = 2 # Max size in MB
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

def get_env_variable(var_name):
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Required environment variable not set: {var_name}")
    return value

MERCADO_PAGO_ACCESS_TOKEN = get_env_variable('CONFIG_MERCADO_PAGO_ACCESS_TOKEN')
MERCADO_PAGO_PUBLIC_KEY = get_env_variable('CONFIG_MERCADO_PAGO_PUBLIC_KEY')
MERCADO_PAGO_CLIENT_ID = get_env_variable('CONFIG_MERCADO_PAGO_CLIENT_ID')
MERCADO_PAGO_CLIENT_SECRET = get_env_variable('CONFIG_MERCADO_PAGO_CLIENT_SECRET')
MERCADO_PAGO_WEBHOOK_SECRET = get_env_variable('CONFIG_MERCADO_PAGO_SIGNATURE')

if not RENDER_EXTERNAL_HOSTNAME:
    raise EnvironmentError(f"Required environment variable not set: RENDER_EXTERNAL_HOSTNAME")

MERCADO_PAGO_SUCCESS_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}/app/payment/mercadopago/sucesso/"
MERCADO_PAGO_FAILURE_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}/app/payment/mercadopago/erro/"

# =========================== STRIPE CONFIGS ===========================

STRIPE_WEBHOOK_SECRET = get_env_variable('CONFIG_STRIPE_WEBHOOK_SECRET')
STRIPE_SECRET_KEY = get_env_variable('CONFIG_STRIPE_SECRET_KEY')

STRIPE_SUCCESS_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}/app/payment/stripe/sucesso/"
STRIPE_FAILURE_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}/app/payment/stripe/erro/"

# =========================== PAYMENTS CONFIGS ===========================

METHODS_PAYMENTS = ["MercadoPago", "Stripe"]
MERCADO_PAGO_ACTIVATE_PAYMENTS = str2bool(get_env_variable('CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS'))
STRIPE_ACTIVATE_PAYMENTS = str2bool(get_env_variable('CONFIG_STRIPE_ACTIVATE_PAYMENTS'))

# =========================== HCAPTCHA CONFIGS ===========================

HCAPTCHA_SITE_KEY = os.environ.get('CONFIG_HCAPTCHA_SITE_KEY')
if not HCAPTCHA_SITE_KEY:
    raise EnvironmentError(f"Required environment variable not set: HCAPTCHA_SITE_KEY")

HCAPTCHA_SECRET_KEY = os.environ.get('CONFIG_HCAPTCHA_SECRET_KEY')
if not HCAPTCHA_SECRET_KEY:
    raise EnvironmentError(f"Required environment variable not set: HCAPTCHA_SECRET_KEY")

# Configuração para número máximo de tentativas de login antes do captcha
LOGIN_MAX_ATTEMPTS = int(os.environ.get('CONFIG_LOGIN_MAX_ATTEMPTS', 3))

# Configuração para comportamento do hCaptcha em caso de falha de rede
# True = permitir registro/login mesmo se hCaptcha falhar (menos seguro)
# False = bloquear registro/login se hCaptcha falhar (mais seguro)
HCAPTCHA_FAIL_OPEN = str2bool(os.environ.get('CONFIG_HCAPTCHA_FAIL_OPEN', False))

# =========================== HEAD CONFIGS ===========================

PROJECT_TITLE = os.getenv('PROJECT_TITLE', 'Lineage 2 PDL')
PROJECT_AUTHOR = os.getenv('PROJECT_AUTHOR', 'Lineage 2 PDL')
PROJECT_DESCRIPTION = os.getenv('PROJECT_DESCRIPTION', 'Painel para servidores privados de Lineage 2.')
PROJECT_KEYWORDS = os.getenv('PROJECT_KEYWORDS', 'lineage l2 painel servidor')
PROJECT_URL = os.getenv('PROJECT_URL', '#')
PROJECT_LOGO_URL = os.getenv('PROJECT_LOGO_URL', '/static/assets/img/logo_painel.png')
PROJECT_FAVICON_ICO = os.getenv('PROJECT_FAVICON_ICO', '/static/assets/img/ico.jpg')
PROJECT_FAVICON_MANIFEST = os.getenv('PROJECT_FAVICON_MANIFEST', '/static/assets/img/favicon/site.webmanifest')
PROJECT_THEME_COLOR = os.getenv('PROJECT_THEME_COLOR', '#ffffff')


# =========================== FOOTER CONFIGS ===========================

PROJECT_DISCORD_URL = os.getenv('PROJECT_DISCORD_URL', 'https://discord.gg/seu-link-aqui')
PROJECT_YOUTUBE_URL = os.getenv('PROJECT_YOUTUBE_URL', 'https://www.youtube.com/@seu-canal')
PROJECT_FACEBOOK_URL = os.getenv('PROJECT_FACEBOOK_URL', 'https://www.facebook.com/sua-pagina')
PROJECT_INSTAGRAM_URL = os.getenv('PROJECT_INSTAGRAM_URL', 'https://www.instagram.com/seu-perfil')

# =========================== OTHERS CONFIGS ===========================

SLOGAN = str2bool(os.getenv('SLOGAN', True))
LINEAGE_QUERY_MODULE = os.getenv('LINEAGE_QUERY_MODULE', 'dreamv3')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'user': '100/minute'
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'apps.api.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'apps.api.exceptions.custom_exception_handler',
}

# DRF Spectacular Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'Lineage 2 API',
    'DESCRIPTION': 'API pública para Lineage 2',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'AUTO_SCHEMA_GENERATION': False,  # Desabilita geração automática de schema
    'TAGS': [],
    
    # Configuração de segurança para Swagger UI
    'SECURITY': [
        {
            'Bearer': []
        }
    ],
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Digite seu token JWT sem o prefixo "Bearer"'
        }
    },
    
    # Template personalizado para Swagger UI
    "SWAGGER_UI_FAVICON_HREF": STATIC_URL + "assets/img/ico.jpg",
}

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

DYNAMIC_API = {
    # SLUG -> Import_PATH 
}

DYNAMIC_DATATB = {
    # SLUG -> Import_PATH 
}

# =========================== SERVER STATUS CONFIGS ===========================

# Configurações para verificação de status do servidor de jogo
GAME_SERVER_IP = os.getenv('GAME_SERVER_IP', '127.0.0.1')
GAME_SERVER_PORT = int(os.getenv('GAME_SERVER_PORT', 7777))
LOGIN_SERVER_PORT = int(os.getenv('LOGIN_SERVER_PORT', 2106))
SERVER_STATUS_TIMEOUT = int(os.getenv('SERVER_STATUS_TIMEOUT', 1))

# Forçar status do servidor (auto = verificação automática, on = sempre online, off = sempre offline)
FORCE_GAME_SERVER_STATUS = os.getenv('FORCE_GAME_SERVER_STATUS', 'auto')
FORCE_LOGIN_SERVER_STATUS = os.getenv('FORCE_LOGIN_SERVER_STATUS', 'auto')

# =========================== JWT CONFIGURATION ===========================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# =========================== JAZZMIN CONFIGURATION ===========================

JAZZMIN_SETTINGS = get_jazzmin_settings(PROJECT_TITLE, PROJECT_LOGO_URL)
JAZZMIN_UI_TWEAKS = get_jazzmin_ui_tweaks()

# =========================== FAKE PLAYERS CONFIGURATION ===========================
FAKE_PLAYERS_FACTOR = float(os.getenv('FAKE_PLAYERS_FACTOR', 1.0))
FAKE_PLAYERS_MIN = int(os.getenv('FAKE_PLAYERS_MIN', 0))
FAKE_PLAYERS_MAX = int(os.getenv('FAKE_PLAYERS_MAX', 0))

# =========================== LICENSE CONFIGURATION ===========================

# Configurações de validação de licenças
LICENSE_CONFIG = {
    'ENCRYPTION_KEY': os.environ.get('PDL_ENCRYPTION_KEY', ''),  # Chave Fernet usada no script gerador
    'DNS_TIMEOUT': int(os.environ.get('PDL_DNS_TIMEOUT', '10')),
}

# Web Push VAPID keys (gere usando pywebpush ou web-push)
# Exemplo para gerar: 
#   from pywebpush import generate_vapid_private_key, generate_vapid_public_key
#   private_key = generate_vapid_private_key()
#   public_key = generate_vapid_public_key(private_key)
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY")
