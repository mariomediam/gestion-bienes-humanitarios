from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_sinpad,
    parse_condicion_persona_id,
    parse_familia_id,
    parse_formulario_2a_id,
    parse_integrante_id,
    parse_persona_id,
)
from app_sgbh.serializers import (
    Formulario2AIntegranteTotalSerializer,
    IntegranteBusquedaSerializer,
    IntegranteCreateSerializer,
    IntegranteSerializer,
    IntegranteUpdateSerializer,
    first_error_message,
)
from app_sgbh.services.formulario_2a_integrante import (
    Formulario2AIntegranteService,
    Formulario2AIntegranteServiceError,
)

_INTEGRANTE_ID_MAX = 2147483647


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
            payload = IntegranteSerializer(created).data
        except Formulario2AIntegranteServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el integrante'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class Formulario2AIntegranteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, integrante_id):
        if integrante_id < 1 or integrante_id > _INTEGRANTE_ID_MAX:
            return Response(
                {'error': 'El campo integrante_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'familia_id' in request.data:
            return Response(
                {'error': 'El campo familia_id no puede modificarse'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'numero_orden' in request.data:
            return Response(
                {'error': 'El campo numero_orden no puede modificarse'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = IntegranteUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated = Formulario2AIntegranteService.update(
                integrante_id,
                **serializer.validated_data,
            )
            payload = IntegranteSerializer(updated).data
        except Formulario2AIntegranteServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo modificar el integrante'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)

    def delete(self, request, integrante_id):
        if integrante_id < 1 or integrante_id > _INTEGRANTE_ID_MAX:
            return Response(
                {'error': 'El campo integrante_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Formulario2AIntegranteService.delete(integrante_id)
        except Formulario2AIntegranteServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo eliminar el integrante'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class Formulario2AIntegranteBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        integrante_id, error = parse_integrante_id(
            request.query_params.get('integrante_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        familia_id, error = parse_familia_id(request.query_params.get('familia_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        persona_id, error = parse_persona_id(request.query_params.get('persona_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        formulario_2a_id, error = parse_formulario_2a_id(
            request.query_params.get('formulario_2a_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo_sinpad, error = parse_codigo_sinpad(
            request.query_params.get('codigo_sinpad')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = Formulario2AIntegranteService.search(
                integrante_id=integrante_id,
                familia_id=familia_id,
                persona_id=persona_id,
                formulario_2a_id=formulario_2a_id,
                codigo_sinpad=codigo_sinpad,
            )
            payload = IntegranteBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de integrantes'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


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
