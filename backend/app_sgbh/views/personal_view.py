from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_es_encargado_almacen,
    parse_es_evaluador_edan,
    parse_esta_activo,
    parse_personal_id,
)
from app_sgbh.serializers import PersonalSerializer
from app_sgbh.services.personal import PersonalService


class PersonalBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(request.query_params)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = PersonalService.search(**parsed)
            payload = PersonalSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de personal'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional personnel search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    """
    parsers = (
        ('personal_id', parse_personal_id),
        ('es_evaluador_edan', parse_es_evaluador_edan),
        ('es_encargado_almacen', parse_es_encargado_almacen),
        ('esta_activo', parse_esta_activo),
    )
    values = {}
    for name, parser in parsers:
        value, error = parser(params.get(name))
        if error:
            return None, error
        values[name] = value

    return values, None
