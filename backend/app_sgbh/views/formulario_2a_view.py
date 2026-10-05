from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_barrio_sector_urbanizacion,
    parse_codigo_sinpad,
    parse_departamento_id,
    parse_distrito_id,
    parse_estado_registro_id,
    parse_localidad,
    parse_optional_date,
    parse_provincia_id,
    parse_tipo_peligro_id,
)
from app_sgbh.serializers import (
    Formulario2ABusquedaSerializer,
    Formulario2ATotalSerializer,
)
from app_sgbh.services.formulario_2a import Formulario2AService


class Formulario2ABuscarView(APIView):
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
            rows = Formulario2AService.search(**parsed)
            payload = Formulario2ABusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de formularios EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


class Formulario2ATotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estado_registro_id, error = parse_estado_registro_id(
            request.query_params.get('estado_registro_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = Formulario2AService.count(estado_registro_id=estado_registro_id)
            payload = Formulario2ATotalSerializer({'total': total}).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de formularios EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional Formulario 2A search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    fecha_desde and fecha_hasta bound fecha_empadronamiento.
    """
    parsers = (
        ('codigo_sinpad', parse_codigo_sinpad),
        ('tipo_peligro_id', parse_tipo_peligro_id),
        ('departamento_id', parse_departamento_id),
        ('provincia_id', parse_provincia_id),
        ('distrito_id', parse_distrito_id),
        ('barrio_sector_urbanizacion', parse_barrio_sector_urbanizacion),
        ('localidad', parse_localidad),
        ('estado_registro_id', parse_estado_registro_id),
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
