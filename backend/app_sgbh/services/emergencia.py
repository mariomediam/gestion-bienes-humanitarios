from django.db.models import Count, F

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

    @staticmethod
    def count_by_tipo_peligro(esta_activo=None):
        """Count emergencies grouped by tipo_peligro_id.

        Joins S43cat_tipos_peligro to include nombre as nombre_peligro.
        Optional filter on S43edan_emergencias.esta_activo.
        """
        queryset = Emergencia.objects.all()
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)
        rows = queryset.values(
            'tipo_peligro_id',
            nombre_peligro=F('tipo_peligro__nombre'),
        ).annotate(total=Count('*'))
        return list(rows)
