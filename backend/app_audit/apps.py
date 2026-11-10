from django.apps import AppConfig


class AppAuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_audit'

    def ready(self):
        # DRF authenticates inside the view, after middleware has already started.
        from app_audit.hooks import install_request_login_hook

        install_request_login_hook()
