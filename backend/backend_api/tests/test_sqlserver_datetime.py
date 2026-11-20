from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from django.conf import settings

from backend_api.sqlserver.operations import DatabaseOperations


class _Connection:
    timezone = ZoneInfo('America/Lima')


def test_adapt_datetimefield_value_uses_the_connection_clock():
    assert settings.USE_TZ is True
    operations = DatabaseOperations(_Connection())
    stored = datetime(2026, 11, 20, 16, 31, 21, tzinfo=timezone.utc)

    adapted = operations.adapt_datetimefield_value(stored)

    assert adapted == datetime(
        2026, 11, 20, 11, 31, 21, tzinfo=ZoneInfo('America/Lima')
    )
