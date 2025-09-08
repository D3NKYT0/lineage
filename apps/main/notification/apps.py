from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main.notification'
    icon = 'fa fa-bell'
    verbose_name = 'Notificações'
