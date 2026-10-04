from django.apps import AppConfig


class AppSgbhConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_sgbh'

    def ready(self):
        from app_sgbh.text_search import register_text_search_lookups

        register_text_search_lookups()
