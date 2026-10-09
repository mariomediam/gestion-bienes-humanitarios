from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers import (
    PersonaCreateSerializer,
    PersonaSerializer,
    first_error_message,
)
from app_sgbh.services.persona import PersonaService, PersonaServiceError


class PersonaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PersonaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = PersonaService.create(
                c_usuari_login=getattr(request.user, 'login', ''),
                **serializer.validated_data,
            )
            payload = PersonaSerializer(created).data
        except PersonaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar la persona'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


_PERSONA_ID_MAX = 2147483647


class PersonaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, persona_id):
        if persona_id < 1 or persona_id > _PERSONA_ID_MAX:
            return Response(
                {'error': 'El campo persona_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PersonaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated = PersonaService.update(
                persona_id,
                **serializer.validated_data,
            )
            payload = PersonaSerializer(updated).data
        except PersonaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo modificar la persona'},
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
