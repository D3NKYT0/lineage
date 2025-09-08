from django.apps import AppConfig


class SimplestatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main.auditor'
    icon = 'fa fa-search'
    verbose_name = 'Auditoria'
