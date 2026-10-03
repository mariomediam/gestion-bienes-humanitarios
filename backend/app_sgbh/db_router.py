"""
Database router for app_sgbh models.

Routes all operations for app_sgbh models to the 'sgbh' database.
"""

APP_LABEL = 'app_sgbh'
DB_ALIAS = 'sgbh'


class SgbhDatabaseRouter:
    """Route app_sgbh queries to the 'sgbh' database connection."""

    def db_for_read(self, model, **hints):
        if model._meta.app_label == APP_LABEL:
            return DB_ALIAS
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == APP_LABEL:
            return DB_ALIAS
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == APP_LABEL
            and obj2._meta.app_label == APP_LABEL
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == APP_LABEL:
            return False
        return None
