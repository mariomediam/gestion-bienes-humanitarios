from django.db.models import Count

from ..models import Formulario2A


class Formulario2AService:
    @staticmethod
    def count(estado_registro_id=None):
        """Count rows in S43edan_formulario_2a.

        Optional filter on estado_registro_id. When omitted, every row is counted.
        """
        queryset = Formulario2A.objects.all()
        if estado_registro_id is not None:
            queryset = queryset.filter(estado_registro_id=estado_registro_id)
        result = queryset.aggregate(total=Count('*'))
        return result['total']
