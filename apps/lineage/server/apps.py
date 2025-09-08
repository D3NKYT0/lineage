from django.apps import AppConfig


class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.lineage.server'
    verbose_name = 'Servidor'

    def ready(self):
        import apps.lineage.server.signals
