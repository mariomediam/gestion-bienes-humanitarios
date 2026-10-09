from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_formulario_2a_id, parse_vivienda_id
from app_sgbh.serializers import (
    ViviendaBusquedaSerializer,
    ViviendaCreateSerializer,
    ViviendaUpdateSerializer,
    first_error_message,
)

_VIVIENDA_ID_MAX = 2147483647
from app_sgbh.services.formulario_2a_vivienda import (
    Formulario2AViviendaService,
    Formulario2AViviendaServiceError,
)


class Formulario2AViviendaCreateView(APIView):
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

        serializer = ViviendaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = Formulario2AViviendaService.create(**serializer.validated_data)
            payload = ViviendaBusquedaSerializer(created).data
        except Formulario2AViviendaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar la vivienda'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class Formulario2AViviendaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, vivienda_id):
        if vivienda_id < 1 or vivienda_id > _VIVIENDA_ID_MAX:
            return Response(
                {'error': 'El campo vivienda_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'formulario_2a_id' in request.data:
            return Response(
                {'error': 'El campo formulario_2a_id no puede modificarse'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if 'numero_orden' in request.data:
            return Response(
                {'error': 'El campo numero_orden no puede modificarse'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ViviendaUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated = Formulario2AViviendaService.update(
                vivienda_id,
                **serializer.validated_data,
            )
            payload = ViviendaBusquedaSerializer(updated).data
        except Formulario2AViviendaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo modificar la vivienda'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)

    def delete(self, request, vivienda_id):
        if vivienda_id < 1 or vivienda_id > _VIVIENDA_ID_MAX:
            return Response(
                {'error': 'El campo vivienda_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Formulario2AViviendaService.delete(vivienda_id)
        except Formulario2AViviendaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo eliminar la vivienda'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class Formulario2AViviendaBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vivienda_id, error = parse_vivienda_id(request.query_params.get('vivienda_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        formulario_2a_id, error = parse_formulario_2a_id(
            request.query_params.get('formulario_2a_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = Formulario2AViviendaService.search(
                vivienda_id=vivienda_id,
                formulario_2a_id=formulario_2a_id,
            )
            payload = ViviendaBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de viviendas'},
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
