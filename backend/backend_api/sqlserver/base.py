"""mssql backend whose datetimes follow the database connection time zone."""

from mssql.base import DatabaseWrapper as MSSQLDatabaseWrapper

from backend_api.sqlserver.operations import DatabaseOperations


class DatabaseWrapper(MSSQLDatabaseWrapper):
    ops_class = DatabaseOperations

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FreeTDS does not keep a datetimeoffset. datetime2 stores the
        # clock time of the connection zone, the same as the S43 columns.
        self.data_types = dict(self.data_types)
        self.data_types['DateTimeField'] = 'datetime2'
