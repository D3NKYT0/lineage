from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.main.home"

    def ready(self):
        import apps.main.home.signals
        import utils.achievements_rules
