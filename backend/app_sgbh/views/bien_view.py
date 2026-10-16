from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_bien_id,
    parse_categoria_bien_id,
    parse_codigo_bien,
    parse_nombre_bien,
    parse_unidad_medida_id,
)
from app_sgbh.serializers import BienBusquedaSerializer
from app_sgbh.services.bien import BienService


class BienBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(request.query_params)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = BienService.search(**parsed)
            payload = BienBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de bienes'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional bienes search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    """
    parsers = (
        ('bien_id', parse_bien_id),
        ('categoria_bien_id', parse_categoria_bien_id),
        ('unidad_medida_id', parse_unidad_medida_id),
        ('codigo', parse_codigo_bien),
        ('nombre', parse_nombre_bien),
    )
    values = {}
    for name, parser in parsers:
        value, error = parser(params.get(name))
        if error:
            return None, error
        values[name] = value

    return values, None
