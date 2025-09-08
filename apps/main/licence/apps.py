from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LicenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main.licence'
    verbose_name = _('Sistema de Licenciamento')

    def ready(self):
        """
        Executado quando o app é carregado
        """
        try:
            # Importa sinais se existirem
            import apps.main.licence.signals
        except ImportError:
            pass
