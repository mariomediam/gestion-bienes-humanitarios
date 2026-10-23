from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_almacen_id,
    parse_bien_id,
    parse_estado_movimiento,
    parse_optional_date,
)
from app_sgbh.serializers.kardex import AlmacenKardexBusquedaSerializer
from app_sgbh.services.kardex import AlmacenKardexService


class AlmacenKardexBuscarView(APIView):
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
            rows = AlmacenKardexService.search(**parsed)
            payload = AlmacenKardexBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda del kardex de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional kardex search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    fecha_desde and fecha_hasta bound fecha_movimiento.
    """
    values = {}
    for name, parser in (
        ('almacen_id', parse_almacen_id),
        ('estado_movimiento', parse_estado_movimiento),
        ('bien_id', parse_bien_id),
    ):
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
