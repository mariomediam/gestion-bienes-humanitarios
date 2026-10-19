from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_anio_planilla,
    parse_barrio_sector_urbanizacion,
    parse_bien_nombre,
    parse_codigo_sinpad,
    parse_documento_referencia,
    parse_integrante_receptor_nombre,
    parse_movimiento_id,
    parse_numero_planilla,
    parse_optional_date,
    parse_planilla_entrega_id,
)
from app_sgbh.serializers.movimiento_planilla_bah import (
    MovimientoPlanillaBahBusquedaSerializer,
)
from app_sgbh.services.movimiento_planilla_bah import MovimientoPlanillaBahService


class MovimientoPlanillaBahBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(request.query_params)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        fecha_desde = parsed['fecha_desde']
        fecha_hasta = parsed['fecha_hasta']
        if (
            fecha_desde is not None
            and fecha_hasta is not None
            and fecha_desde > fecha_hasta
        ):
            return Response(
                {'error': 'El filtro fecha_desde no puede ser posterior a fecha_hasta'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            rows = MovimientoPlanillaBahService.search(**parsed)
            payload = MovimientoPlanillaBahBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {
                    'error': (
                        'No se pudo obtener la búsqueda de movimientos '
                        'de planilla BAH'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional BAH planilla movement search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    fecha_desde and fecha_hasta bound fecha_entrega.
    """
    parsers = (
        ('planilla_entrega_id', parse_planilla_entrega_id),
        ('movimiento_id', parse_movimiento_id),
        ('numero_planilla', parse_numero_planilla),
        ('anio_planilla', parse_anio_planilla),
        ('codigo_sinpad', parse_codigo_sinpad),
        ('barrio_sector_urbanizacion', parse_barrio_sector_urbanizacion),
        ('documento_referencia', parse_documento_referencia),
        ('integrante_receptor_nombre', parse_integrante_receptor_nombre),
        ('bien_nombre', parse_bien_nombre),
    )
    values = {}
    for name, parser in parsers:
        value, error = parser(params.get(name))
        if error:
            return None, error
        values[name] = value

    fecha_desde, error = parse_optional_date(params.get('fecha_desde'), 'fecha_desde')
    if error:
        return None, error
    fecha_hasta, error = parse_optional_date(params.get('fecha_hasta'), 'fecha_hasta')
    if error:
        return None, error

    values['fecha_desde'] = fecha_desde
    values['fecha_hasta'] = fecha_hasta
    return values, None
