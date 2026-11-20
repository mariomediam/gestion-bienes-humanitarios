"""Session options required by SQL Server through FreeTDS.

ODBC leaves ARITHABORT OFF. INSERT, UPDATE and DELETE then fail with
error 1934 on any table that has a filtered index, including
django_content_type and several S43 unique indexes. SQL Server 2022
still enforces that session setting.

SET ARITHABORT needs a schema-stability lock. An open transaction on
the same database (often an SSMS window left uncommitted) blocks it,
and sys.sysprocesses shows the wait as SET OPTION ON. The lock timeout
stops that wait from holding the request until the blocker ends.
"""

# Wait at most 15 seconds for the schema lock, then restore the default.
_ARITHABORT_LOCK_TIMEOUT_MS = 15000


def enable_arithabort(sender, connection, **kwargs):
    """Turn ARITHABORT on for one new SQL Server connection."""
    if connection.vendor != 'microsoft':
        return
    with connection.cursor() as cursor:
        cursor.execute(f'SET LOCK_TIMEOUT {_ARITHABORT_LOCK_TIMEOUT_MS}')
        try:
            cursor.execute('SET ARITHABORT ON')
        finally:
            cursor.execute('SET LOCK_TIMEOUT -1')
