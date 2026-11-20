from app_sgbh.sqlserver import enable_arithabort


class _Cursor:
    def __init__(self):
        self.statements = []

    def execute(self, sql):
        self.statements.append(sql)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class _Connection:
    def __init__(self, vendor):
        self.vendor = vendor
        self.cursor_obj = _Cursor()

    def cursor(self):
        return self.cursor_obj


def test_enable_arithabort_on_sql_server():
    connection = _Connection('microsoft')

    enable_arithabort(sender=None, connection=connection)

    assert connection.cursor_obj.statements == ['SET ARITHABORT ON']


def test_enable_arithabort_ignores_other_vendors():
    connection = _Connection('postgresql')

    enable_arithabort(sender=None, connection=connection)

    assert connection.cursor_obj.statements == []
