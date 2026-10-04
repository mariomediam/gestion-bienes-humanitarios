from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_barrio_sector_urbanizacion,
    parse_codigo_sinpad,
    parse_distrito_nombre,
    parse_emergencia_id,
    parse_esta_activo,
    parse_fecha_desde,
    parse_localidad,
    parse_numero_evaluacion,
    parse_optional_date,
    parse_tipo_peligro_id,
)
from app_sgbh.serializers import (
    EmergenciaCreateSerializer,
    EmergenciaSerializer,
    first_error_message,
)
from app_sgbh.services.emergencia import EmergenciaService, EmergenciaServiceError


class EmergenciaTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = EmergenciaService.count(esta_activo=esta_activo)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de emergencias'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({'total': total}, status=status.HTTP_200_OK)


class EmergenciaTotalPorTipoPeligroView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = EmergenciaService.count_by_tipo_peligro(esta_activo=esta_activo)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de emergencias por tipo de peligro'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(rows, status=status.HTTP_200_OK)


class EmergenciaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_desde, error = parse_fecha_desde(request.query_params.get('fecha_desde'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = EmergenciaService.list_from_date(fecha_desde)
            payload = EmergenciaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el listado de emergencias'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EmergenciaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = EmergenciaService.create(
                c_usuari_login=getattr(request.user, 'login', ''),
                **serializer.validated_data,
            )
            payload = EmergenciaSerializer(created).data
        except EmergenciaServiceError as exc:
            http_status = (
                status.HTTP_409_CONFLICT if exc.conflict else status.HTTP_400_BAD_REQUEST
            )
            return Response({'error': exc.message}, status=http_status)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar la emergencia'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class EmergenciaBuscarView(APIView):
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
            rows = EmergenciaService.search(**parsed)
            payload = EmergenciaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de emergencias'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional emergency search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    """
    parsers = (
        ('emergencia_id', parse_emergencia_id),
        ('codigo_sinpad', parse_codigo_sinpad),
        ('barrio_sector_urbanizacion', parse_barrio_sector_urbanizacion),
        ('numero_evaluacion', parse_numero_evaluacion),
        ('tipo_peligro_id', parse_tipo_peligro_id),
        ('localidad', parse_localidad),
        ('distrito_nombre', parse_distrito_nombre),
        ('esta_activo', parse_esta_activo),
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
