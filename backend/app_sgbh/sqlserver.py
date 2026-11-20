"""Session options required by SQL Server 2008 R2 through FreeTDS.

ODBC leaves ARITHABORT OFF. INSERT, UPDATE and DELETE then fail with
error 1934 on any table that has a filtered index, including
django_content_type and several S43 unique indexes.
"""

def enable_arithabort(sender, connection, **kwargs):
    """Turn ARITHABORT on for one new SQL Server connection."""
    if connection.vendor != 'microsoft':
        return
    with connection.cursor() as cursor:
        cursor.execute('SET ARITHABORT ON')
