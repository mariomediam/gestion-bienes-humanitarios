from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_almacen_id,
    parse_bien_nombre,
    parse_documento_origen_referencia,
    parse_documento_referencia,
    parse_estado_movimiento_id,
    parse_movimiento_id,
    parse_movimiento_origen_id,
    parse_numero_planilla,
    parse_optional_date,
)
from app_sgbh.serializers.movimiento_devolucion import (
    MovimientoDevolucionBusquedaSerializer,
)
from app_sgbh.services.movimiento_devolucion import MovimientoDevolucionService


class MovimientoDevolucionBuscarView(APIView):
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
                {
                    'error': (
                        'El filtro fecha_desde no puede ser posterior a fecha_hasta'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        fecha_documento_desde = parsed['fecha_documento_desde']
        fecha_documento_hasta = parsed['fecha_documento_hasta']
        if (
            fecha_documento_desde is not None
            and fecha_documento_hasta is not None
            and fecha_documento_desde > fecha_documento_hasta
        ):
            return Response(
                {
                    'error': (
                        'El filtro fecha_documento_desde no puede ser posterior '
                        'a fecha_documento_hasta'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            rows = MovimientoDevolucionService.search(**parsed)
            payload = MovimientoDevolucionBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de devoluciones'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional devolución search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    fecha_movimiento is one calendar day. fecha_desde and fecha_hasta bound
    fecha_movimiento. fecha_documento_desde and fecha_documento_hasta bound
    fecha_documento.
    """
    parsers = (
        ('movimiento_id', parse_movimiento_id),
        ('almacen_id', parse_almacen_id),
        ('estado_movimiento_id', parse_estado_movimiento_id),
        ('movimiento_origen_id', parse_movimiento_origen_id),
        ('documento_referencia', parse_documento_referencia),
        ('documento_origen_referencia', parse_documento_origen_referencia),
        ('numero_planilla', parse_numero_planilla),
        ('bien_nombre', parse_bien_nombre),
    )
    values = {}
    for name, parser in parsers:
        value, error = parser(params.get(name))
        if error:
            return None, error
        values[name] = value

    fecha_movimiento, error = parse_optional_date(
        params.get('fecha_movimiento'),
        'fecha_movimiento',
    )
    if error:
        return None, error
    fecha_documento_desde, error = parse_optional_date(
        params.get('fecha_documento_desde'),
        'fecha_documento_desde',
    )
    if error:
        return None, error
    fecha_documento_hasta, error = parse_optional_date(
        params.get('fecha_documento_hasta'),
        'fecha_documento_hasta',
    )
    if error:
        return None, error

    fecha_desde, error = parse_optional_date(params.get('fecha_desde'), 'fecha_desde')
    if error:
        return None, error
    fecha_hasta, error = parse_optional_date(params.get('fecha_hasta'), 'fecha_hasta')
    if error:
        return None, error

    values['fecha_movimiento'] = fecha_movimiento
    values['fecha_documento_desde'] = fecha_documento_desde
    values['fecha_documento_hasta'] = fecha_documento_hasta
    values['fecha_desde'] = fecha_desde
    values['fecha_hasta'] = fecha_hasta
    return values, None
