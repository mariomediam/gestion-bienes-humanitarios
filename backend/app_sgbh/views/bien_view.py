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
from app_sgbh.serializers import (
    BienBusquedaSerializer,
    BienUpdateSerializer,
    first_error_message,
)
from app_sgbh.services.bien import BienService, BienServiceError


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


_BIEN_ID_MAX = 2147483647


class BienDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, bien_id):
        if bien_id < 1 or bien_id > _BIEN_ID_MAX:
            return Response(
                {'error': 'El campo bien_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BienUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated = BienService.update(bien_id, **serializer.validated_data)
            payload = BienBusquedaSerializer(updated).data
        except BienServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo modificar el bien'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _respuesta_error_servicio(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)


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
