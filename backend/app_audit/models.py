from django.db import models

from auditlog.models import AbstractLogEntry

from app_audit.fields import JsonTextField


class AuditLogEntry(AbstractLogEntry):
    """One INSERT, UPDATE or DELETE recorded by django-auditlog.

    actor stays empty: this system has no Django user. The person who made
    the change is the institutional login stored in c_usuari_login.
    """

    # Not a foreign key: this system does not use Django users, and GENERAL
    # must not gain the auth_user table just to store an empty actor.
    actor = models.PositiveIntegerField(blank=True, null=True)
    serialized_data = JsonTextField(null=True, blank=True)
    changes = JsonTextField(null=True, blank=True)
    additional_data = JsonTextField(null=True, blank=True)
    c_usuari_login = models.CharField(max_length=20, blank=True, default='', db_index=True)

    class Meta(AbstractLogEntry.Meta):
        abstract = False
        db_table = 'auditlog_logentry'
