from django.apps import AppConfig


class MapxAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mapx_app'

    def ready(self):
        import mapx_app.signals  # Import signals module