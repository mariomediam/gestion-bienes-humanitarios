"""Keep the audit log on the default connection (GENERAL)."""


class AuditDatabaseRouter:
    """Route auditlog tables to GENERAL and skip them on SIAC."""

    APP_LABELS = {'app_audit', 'auditlog'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.APP_LABELS:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.APP_LABELS:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.APP_LABELS:
            return db == 'default'
        return None
