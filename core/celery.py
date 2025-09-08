from __future__ import absolute_import, unicode_literals

import os
from str2bool import str2bool

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Verifica se está em modo DEBUG
DEBUG = str2bool(os.environ.get('DEBUG', False))

app = Celery("core")

# Configuração especial para modo DEBUG
if DEBUG:
    # Configurações para modo desenvolvimento sem Redis
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url='memory://',
        result_backend='cache+memory://',
        # Configurações para evitar timeouts e erros de conexão
        broker_connection_retry_on_startup=False,
        broker_connection_retry=False,
    )
else:
    # Configuração normal para produção
    app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
