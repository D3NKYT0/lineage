from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main.news'
    icon = 'fa fa-newspaper'
    verbose_name = 'Notícias'
