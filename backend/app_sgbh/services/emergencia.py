from django.db import connections, router

from ..models import Emergencia

_COUNT_SQL = 'SELECT COUNT(*) AS total FROM S43edan_emergencias'
_COUNT_BY_ACTIVE_SQL = (
    'SELECT COUNT(*) AS total FROM S43edan_emergencias WHERE esta_activo = %s'
)


class EmergenciaService:
    @staticmethod
    def count(esta_activo=None):
        """Count rows in S43edan_emergencias.

        Optional filter on esta_activo. When omitted, every row is counted.
        """
        db_alias = router.db_for_read(Emergencia)
        if esta_activo is None:
            sql = _COUNT_SQL
            params = []
        else:
            sql = _COUNT_BY_ACTIVE_SQL
            params = [1 if esta_activo else 0]

        with connections[db_alias].cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
        return row[0]
