from django.apps import AppConfig


class AdministratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.main.administrator'
    icon = 'fa fa-shield-alt'
    verbose_name = 'Administração'
