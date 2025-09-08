import os
from str2bool import str2bool

# Só importa e configura o Celery se não estiver em modo DEBUG
DEBUG = str2bool(os.environ.get('DEBUG', False))

if not DEBUG:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
else:
    # Em modo DEBUG, cria um mock do celery_app para evitar erros
    celery_app = None
    __all__ = ('celery_app',)
