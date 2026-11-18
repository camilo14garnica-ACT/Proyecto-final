from django.apps import AppConfig


class CalidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calidad'
    verbose_name = 'Gestión de Calidad'

    def ready(self):
        import calidad.signals  # noqa
