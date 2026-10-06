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
    parse_formulario_2a_id,
    parse_localidad,
    parse_optional_date,
    parse_provincia_id,
    parse_tipo_peligro_id,
)
from app_sgbh.serializers import (
    Formulario2ABusquedaSerializer,
    Formulario2ACreateSerializer,
    Formulario2ADetalleSerializer,
    Formulario2ATotalSerializer,
    Formulario2AUpdateSerializer,
    first_error_message,
)

_FORMULARIO_2A_ID_MAX = 2147483647
from app_sgbh.services.formulario_2a import (
    Formulario2AService,
    Formulario2AServiceError,
)


class Formulario2ACreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = Formulario2ACreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = Formulario2AService.create(
                c_usuari_login=getattr(request.user, 'login', ''),
                **serializer.validated_data,
            )
            payload = Formulario2ABusquedaSerializer(created).data
        except Formulario2AServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el formulario EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class Formulario2ADetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, formulario_2a_id):
        if formulario_2a_id < 1 or formulario_2a_id > _FORMULARIO_2A_ID_MAX:
            return Response(
                {'error': 'El campo formulario_2a_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            formulario = Formulario2AService.get(formulario_2a_id)
            payload = Formulario2ADetalleSerializer(formulario).data
        except Formulario2AServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el formulario EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)

    def put(self, request, formulario_2a_id):
        if formulario_2a_id < 1 or formulario_2a_id > _FORMULARIO_2A_ID_MAX:
            return Response(
                {'error': 'El campo formulario_2a_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'emergencia_id' in request.data:
            return Response(
                {'error': 'El campo emergencia_id no puede modificarse'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = Formulario2AUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated = Formulario2AService.update(
                formulario_2a_id,
                **serializer.validated_data,
            )
            payload = Formulario2ADetalleSerializer(updated).data
        except Formulario2AServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo modificar el formulario EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


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


def _respuesta_error_servicio(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    elif exc.conflict:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)


def _parse_busqueda(params):
    """Parse optional Formulario 2A search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    fecha_desde and fecha_hasta bound fecha_empadronamiento.
    """
    parsers = (
        ('formulario_2a_id', parse_formulario_2a_id),
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
