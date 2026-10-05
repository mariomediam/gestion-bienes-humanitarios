from django.db.models import CharField, Count, OuterRef, Prefetch, Subquery

from ..models import Distrito, Formulario2A, Formulario2AVivienda
from ..text_search import filter_text_like


class Formulario2AService:
    @staticmethod
    def search(
        codigo_sinpad=None,
        tipo_peligro_id=None,
        departamento_id=None,
        provincia_id=None,
        distrito_id=None,
        fecha_desde=None,
        fecha_hasta=None,
        barrio_sector_urbanizacion=None,
        localidad=None,
        estado_registro_id=None,
    ):
        """Return Formulario 2A rows using optional filters combined with AND.

        fecha_desde and fecha_hasta restrict fecha_empadronamiento.
        barrio_sector_urbanizacion and localidad use a case-insensitive
        partial match. The other filters are exact.
        Ordered by fecha_empadronamiento and hora_empadronamiento descending.
        Each row includes the emergency, the hazard name, distrito_nombre,
        the evaluator name and its viviendas. With no filters, every row
        is returned. The queryset is ready for Formulario2ABusquedaSerializer.
        """
        queryset = _formularios_busqueda()
        if codigo_sinpad is not None:
            queryset = queryset.filter(emergencia__codigo_sinpad=codigo_sinpad)
        if tipo_peligro_id is not None:
            queryset = queryset.filter(emergencia__tipo_peligro_id=tipo_peligro_id)
        if departamento_id is not None:
            queryset = queryset.filter(departamento_id=departamento_id)
        if provincia_id is not None:
            queryset = queryset.filter(provincia_id=provincia_id)
        if distrito_id is not None:
            queryset = queryset.filter(distrito_id=distrito_id)
        if fecha_desde is not None:
            queryset = queryset.filter(fecha_empadronamiento__gte=fecha_desde)
        if fecha_hasta is not None:
            queryset = queryset.filter(fecha_empadronamiento__lte=fecha_hasta)
        if barrio_sector_urbanizacion is not None:
            queryset = filter_text_like(
                queryset,
                'barrio_sector_urbanizacion',
                barrio_sector_urbanizacion,
            )
        if localidad is not None:
            queryset = filter_text_like(queryset, 'localidad', localidad)
        if estado_registro_id is not None:
            queryset = queryset.filter(estado_registro_id=estado_registro_id)

        return queryset.order_by('-fecha_empadronamiento', '-hora_empadronamiento')

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


def _formularios_busqueda():
    """Formulario 2A rows with distrito_nombre and nested viviendas.

    distrito_nombre comes from DISTRITO matched by the three ubigeo codes.
    Viviendas stay on the parent row instead of duplicating the formulario.
    """
    distrito_nombre = Distrito.objects.filter(
        departamento_id=OuterRef('departamento_id'),
        provincia_id=OuterRef('provincia_id'),
        distrito_id=OuterRef('distrito_id'),
    ).values('distrito_nombre')[:1]
    viviendas = Formulario2AVivienda.objects.order_by('numero_orden', 'vivienda_id')
    return (
        Formulario2A.objects.annotate(
            distrito_nombre=Subquery(distrito_nombre, output_field=CharField())
        )
        .select_related('emergencia', 'emergencia__tipo_peligro', 'evaluador')
        .prefetch_related(Prefetch('viviendas', queryset=viviendas))
    )
