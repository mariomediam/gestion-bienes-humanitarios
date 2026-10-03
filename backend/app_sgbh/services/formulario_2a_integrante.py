from django.db.models import Count

from ..models import Formulario2AIntegrante


class Formulario2AIntegranteService:
    @staticmethod
    def count(condicion_persona_id=None):
        """Count rows in S43edan_formulario_2a_integrantes.

        Optional filter on condicion_persona_id. When omitted, every row is counted.
        """
        queryset = Formulario2AIntegrante.objects.all()
        if condicion_persona_id is not None:
            queryset = queryset.filter(condicion_persona_id=condicion_persona_id)
        result = queryset.aggregate(total=Count('*'))
        return result['total']
