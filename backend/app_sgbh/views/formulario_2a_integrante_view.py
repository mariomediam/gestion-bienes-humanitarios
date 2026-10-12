from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_condicion_persona_id
from app_sgbh.serializers import (
    Formulario2AIntegranteTotalSerializer,
    IntegranteBusquedaSerializer,
    IntegranteCreateSerializer,
    first_error_message,
)
from app_sgbh.services.formulario_2a_integrante import (
    Formulario2AIntegranteService,
    Formulario2AIntegranteServiceError,
)


class Formulario2AIntegranteCreateView(APIView):
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

        serializer = IntegranteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = Formulario2AIntegranteService.create(
                **serializer.validated_data
            )
            payload = IntegranteBusquedaSerializer(created).data
        except Formulario2AIntegranteServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el integrante'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class Formulario2AIntegranteTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        condicion_persona_id, error = parse_condicion_persona_id(
            request.query_params.get('condicion_persona_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = Formulario2AIntegranteService.count(
                condicion_persona_id=condicion_persona_id
            )
            payload = Formulario2AIntegranteTotalSerializer({'total': total}).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de integrantes'},
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
