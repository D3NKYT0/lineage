from django.apps import AppConfig
from django.core.management import call_command
from django.db.utils import OperationalError
import logging
import sys
import os

logger = logging.getLogger(__name__)

# Flag global para evitar execução múltipla
_populate_resources_executed = False


class ResourcesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main.resources'
    verbose_name = 'Recursos do Sistema'

    def ready(self):
        """
        Executa o comando populate_resources automaticamente quando a aplicação inicia.
        Usa request_started para evitar warning de acesso ao banco durante inicialização.
        """
        global _populate_resources_executed

        # Evita executar durante migrations, makemigrations, collectstatic, test, etc.
        excluded_commands = [
            'migrate', 'makemigrations', 'collectstatic', 'test',
            'shell', 'shell_plus', 'dbshell', 'sqlmigrate', 'showmigrations'
        ]

        if any(cmd in sys.argv for cmd in excluded_commands):
            return

        # Evita executar em processos de worker do Celery
        if 'celery' in sys.argv[0] or 'celery' in ' '.join(sys.argv):
            return

        # Verifica se está rodando em ambiente de teste
        if os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('.test_settings'):
            return

        # Usa post_migrate para migrate; request_started para runserver/gunicorn/daphne
        from django.db.models.signals import post_migrate
        from django.core.signals import request_started

        def populate_resources_handler(sender=None, **kwargs):
            """Handler que popula recursos (sem acesso ao DB até ser chamado)."""
            global _populate_resources_executed
            if _populate_resources_executed:
                return

            try:
                logger.info("🔄 Populando recursos do sistema...")
                call_command('populate_resources', verbosity=0)
                _populate_resources_executed = True
                logger.info("✅ Recursos do sistema populados com sucesso!")
            except (OperationalError, Exception) as e:
                logger.error(f"❌ Erro ao popular recursos do sistema: {e}")

        # Conecta post_migrate (roda após migrate)
        if not hasattr(ResourcesConfig, '_post_migrate_connected'):
            post_migrate.connect(populate_resources_handler, sender=self, weak=False)
            ResourcesConfig._post_migrate_connected = True

        # Para runserver/gunicorn/daphne: executa no primeiro request (apps já prontos)
        if 'runserver' in sys.argv or 'daphne' in sys.argv[0] or 'gunicorn' in sys.argv[0]:
            if not hasattr(ResourcesConfig, '_request_connected'):
                def on_first_request(sender, **kwargs):
                    populate_resources_handler(sender=self)
                    request_started.disconnect(on_first_request)

                request_started.connect(on_first_request)
                ResourcesConfig._request_connected = True
