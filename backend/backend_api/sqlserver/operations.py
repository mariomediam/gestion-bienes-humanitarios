"""Datetime adaptation for columns that keep the server's local clock."""

from django.conf import settings
from django.utils import timezone
from mssql.operations import DatabaseOperations as MSSQLDatabaseOperations


class DatabaseOperations(MSSQLDatabaseOperations):
    def adapt_datetimefield_value(self, value):
        """Send the connection clock time instead of UTC.

        FreeTDS stores the wall time and drops the offset on datetime and
        datetime2. Those SIAC columns follow GETDATE() and SYSDATETIME(),
        which on this server are America/Lima. Converting to UTC first
        leaves the stored clock five hours ahead of the local time.
        """
        if value is None:
            return None
        if hasattr(value, 'resolve_expression'):
            return value
        if timezone.is_aware(value) and settings.USE_TZ:
            return value.astimezone(self.connection.timezone)
        return super().adapt_datetimefield_value(value)
