from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_departamento_id,
    parse_distrito_id,
    parse_distrito_nombre,
    parse_f_activo,
    parse_provincia_id,
)
from app_sgbh.serializers import DistritoSerializer
from app_sgbh.services.distrito import DistritoService

_FILTROS = (
    ('departamento_id', parse_departamento_id),
    ('provincia_id', parse_provincia_id),
    ('distrito_id', parse_distrito_id),
    ('distrito_nombre', parse_distrito_nombre),
    ('f_activo', parse_f_activo),
)


class DistritoBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(request.query_params)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = DistritoService.search(**parsed)
            payload = DistritoSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de distritos'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional district search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    """
    values = {}
    for name, parser in _FILTROS:
        value, error = parser(params.get(name))
        if error:
            return None, error
        values[name] = value

    return values, None
