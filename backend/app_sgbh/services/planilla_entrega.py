from django.db.models import Count

from ..models import PlanillaEntrega


class PlanillaEntregaService:
    @staticmethod
    def count(estado_planilla_id=None):
        """Count rows in S43bah_planilla_entrega.

        Optional filter on estado_planilla_id. When omitted, every row is counted.
        """
        queryset = PlanillaEntrega.objects.all()
        if estado_planilla_id is not None:
            queryset = queryset.filter(estado_planilla_id=estado_planilla_id)
        result = queryset.aggregate(total=Count('*'))
        return result['total']
