from django.apps import AppConfig


class FaqConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main.faq'
    icon = 'fa fa-question-circle'
    verbose_name = 'Ajuda (FAQ)'
