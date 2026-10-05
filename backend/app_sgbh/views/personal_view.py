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

_FILTROS = (
    ('personal_id', parse_personal_id),
    ('es_evaluador_edan', parse_es_evaluador_edan),
    ('es_encargado_almacen', parse_es_encargado_almacen),
    ('esta_activo', parse_esta_activo),
)


class PersonalBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(request.query_params)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return _responder_busqueda(
            parsed,
            'No se pudo obtener la búsqueda de personal',
        )


class PersonalEvaluadoresBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(
            request.query_params,
            omit=('es_evaluador_edan',),
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        parsed['es_evaluador_edan'] = True
        return _responder_busqueda(
            parsed,
            'No se pudo obtener la búsqueda de evaluadores',
        )


class PersonalEncargadosAlmacenBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(
            request.query_params,
            omit=('es_encargado_almacen',),
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        parsed['es_encargado_almacen'] = True
        return _responder_busqueda(
            parsed,
            'No se pudo obtener la búsqueda de encargados de almacén',
        )


def _responder_busqueda(parsed, error_message):
    try:
        rows = PersonalService.search(**parsed)
        payload = PersonalSerializer(rows, many=True).data
    except Exception:
        return Response(
            {'error': error_message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params, omit=()):
    """Parse optional personnel search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    Names in omit are left out so the caller can fix that filter.
    """
    values = {}
    for name, parser in _FILTROS:
        if name in omit:
            continue
        value, error = parser(params.get(name))
        if error:
            return None, error
        values[name] = value

    return values, None
