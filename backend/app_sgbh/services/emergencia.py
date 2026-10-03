from django.db.models import Count

from ..models import Emergencia


class EmergenciaService:
    @staticmethod
    def count(esta_activo=None):
        """Count rows in S43edan_emergencias.

        Optional filter on esta_activo. When omitted, every row is counted.
        """
        queryset = Emergencia.objects.all()
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)
        result = queryset.aggregate(total=Count('*'))
        return result['total']
