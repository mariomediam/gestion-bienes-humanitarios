from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_almacen_id,
    parse_bien_nombre,
    parse_destinatario,
    parse_documento_referencia,
    parse_encargado_almacen_id,
    parse_estado_movimiento_id,
    parse_movimiento_id,
    parse_movimiento_origen_id,
    parse_observacion,
    parse_optional_date,
    parse_tipo_movimiento_id,
)
from app_sgbh.serializers.movimiento import (
    MovimientoBusquedaSerializer,
    MovimientoCreateSerializer,
    MovimientoSerializer,
    MovimientoUpdateSerializer,
)

_MOVIMIENTO_ID_MAX = 2147483647
from app_sgbh.services.movimiento import MovimientoService, MovimientoServiceError


class MovimientoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MovimientoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': _first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = MovimientoService.create(
                c_usuari_login=getattr(request.user, 'login', ''),
                **serializer.validated_data,
            )
            payload = MovimientoSerializer(created).data
        except MovimientoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el movimiento de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class MovimientoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, movimiento_id):
        if movimiento_id < 1 or movimiento_id > _MOVIMIENTO_ID_MAX:
            return Response(
                {'error': 'El campo movimiento_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MovimientoUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': _first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated = MovimientoService.update(
                movimiento_id,
                c_usuari_login=getattr(request.user, 'login', ''),
                **serializer.validated_data,
            )
            payload = MovimientoSerializer(updated).data
        except MovimientoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo modificar el movimiento de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


class MovimientoBuscarView(APIView):
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
            rows = MovimientoService.search(**parsed)
            payload = MovimientoBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de movimientos de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional warehouse movement search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    fecha_desde and fecha_hasta bound fecha_movimiento.
    """
    parsers = (
        ('movimiento_id', parse_movimiento_id),
        ('almacen_id', parse_almacen_id),
        ('tipo_movimiento_id', parse_tipo_movimiento_id),
        ('estado_movimiento_id', parse_estado_movimiento_id),
        ('movimiento_origen_id', parse_movimiento_origen_id),
        ('documento_referencia', parse_documento_referencia),
        ('destinatario', parse_destinatario),
        ('observacion', parse_observacion),
        ('encargado_almacen_id', parse_encargado_almacen_id),
        ('bien_nombre', parse_bien_nombre),
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


def _respuesta_error_servicio(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    elif exc.conflict:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)


def _first_error_message(errors):
    """Return the first nested serializer error as one Spanish message."""
    if isinstance(errors, dict):
        for value in errors.values():
            message = _first_error_message(value)
            if message:
                return message
    elif isinstance(errors, (list, tuple)):
        for item in errors:
            message = _first_error_message(item)
            if message:
                return message
    elif errors:
        return str(errors)
    return 'Los datos enviados no son válidos'
