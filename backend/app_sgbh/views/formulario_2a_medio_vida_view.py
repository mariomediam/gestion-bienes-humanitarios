from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_familia_id,
    parse_medio_vida_id,
    parse_tipo_medio_vida_id,
)
from app_sgbh.serializers import (
    MedioVidaBusquedaSerializer,
    MedioVidaCreateSerializer,
    MedioVidaSerializer,
    MedioVidaUpdateSerializer,
    first_error_message,
)

_MEDIO_VIDA_ID_MAX = 2147483647
from app_sgbh.services.formulario_2a_medio_vida import (
    Formulario2AMedioVidaService,
    Formulario2AMedioVidaServiceError,
)


class Formulario2AMedioVidaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MedioVidaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = Formulario2AMedioVidaService.create(
                **serializer.validated_data
            )
            payload = MedioVidaSerializer(created).data
        except Formulario2AMedioVidaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el medio de vida'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class Formulario2AMedioVidaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, medio_vida_id):
        if medio_vida_id < 1 or medio_vida_id > _MEDIO_VIDA_ID_MAX:
            return Response(
                {'error': 'El campo medio_vida_id debe ser un número entero'},
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

        serializer = MedioVidaUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated = Formulario2AMedioVidaService.update(
                medio_vida_id,
                **serializer.validated_data,
            )
            payload = MedioVidaSerializer(updated).data
        except Formulario2AMedioVidaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo modificar el medio de vida'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)

    def delete(self, request, medio_vida_id):
        if medio_vida_id < 1 or medio_vida_id > _MEDIO_VIDA_ID_MAX:
            return Response(
                {'error': 'El campo medio_vida_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Formulario2AMedioVidaService.delete(medio_vida_id)
        except Formulario2AMedioVidaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo eliminar el medio de vida'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class Formulario2AMedioVidaBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        medio_vida_id, error = parse_medio_vida_id(
            request.query_params.get('medio_vida_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        familia_id, error = parse_familia_id(request.query_params.get('familia_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        tipo_medio_vida_id, error = parse_tipo_medio_vida_id(
            request.query_params.get('tipo_medio_vida_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = Formulario2AMedioVidaService.search(
                medio_vida_id=medio_vida_id,
                familia_id=familia_id,
                tipo_medio_vida_id=tipo_medio_vida_id,
            )
            payload = MedioVidaBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de medios de vida'},
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
