from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers.movimiento import (
    MovimientoCreateSerializer,
    MovimientoSerializer,
)
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
            created = MovimientoService.create(**serializer.validated_data)
            payload = MovimientoSerializer(created).data
        except MovimientoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el movimiento de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


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
