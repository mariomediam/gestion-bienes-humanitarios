from django.apps import AppConfig


class AppSgbhConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_sgbh'

    def ready(self):
        from django.db.backends.signals import connection_created

        from app_sgbh.sqlserver import enable_arithabort
        from app_sgbh.text_search import register_text_search_lookups

        register_text_search_lookups()
        connection_created.connect(
            enable_arithabort,
            dispatch_uid='app_sgbh.enable_arithabort',
        )
