from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers import (
    FamiliaCreateSerializer,
    FamiliaSerializer,
    first_error_message,
)
from app_sgbh.services.formulario_2a_familia import (
    Formulario2AFamiliaService,
    Formulario2AFamiliaServiceError,
)

_FAMILIA_ID_MAX = 2147483647


class Formulario2AFamiliaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'numero_orden' in request.data:
            return Response(
                {'error': 'El campo numero_orden lo asigna el sistema'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FamiliaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = Formulario2AFamiliaService.create(**serializer.validated_data)
            payload = FamiliaSerializer(created).data
        except Formulario2AFamiliaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar la familia'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class Formulario2AFamiliaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, familia_id):
        if familia_id < 1 or familia_id > _FAMILIA_ID_MAX:
            return Response(
                {'error': 'El campo familia_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Formulario2AFamiliaService.delete(familia_id)
        except Formulario2AFamiliaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo eliminar la familia'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


def _respuesta_error_servicio(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    elif exc.conflict:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)
