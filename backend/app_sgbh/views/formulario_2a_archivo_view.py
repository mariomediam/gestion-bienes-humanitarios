from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers import Formulario2AArchivoSerializer
from app_sgbh.services.formulario_2a_archivo import (
    Formulario2AArchivoService,
    Formulario2AArchivoServiceError,
)

_FORMULARIO_2A_ID_MAX = 2147483647
_ARCHIVO_ID_MAX = 9223372036854775807
_CAMPOS_DEL_SISTEMA = (
    'archivo_id',
    'formulario_2a_id',
    'nombre_original',
    'nombre_archivo',
    'ruta_archivo',
    'extension',
    'tamano_bytes',
    'esta_activo',
    'fecha_registro',
    'c_usuari_login',
)


class Formulario2AArchivoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, formulario_2a_id):
        if formulario_2a_id < 1 or formulario_2a_id > _FORMULARIO_2A_ID_MAX:
            return Response(
                {'error': 'El campo formulario_2a_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not hasattr(request.data, 'keys'):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for campo in _CAMPOS_DEL_SISTEMA:
            if campo in request.data:
                return Response(
                    {'error': f'El campo {campo} lo asigna el sistema'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        archivos = request.FILES.getlist('archivo')
        if not archivos:
            return Response(
                {'error': 'El archivo es obligatorio'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(archivos) > 1:
            return Response(
                {'error': 'Solo se puede subir un archivo por solicitud'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = Formulario2AArchivoService.create(
                formulario_2a_id=formulario_2a_id,
                archivo=archivos[0],
                c_usuari_login=getattr(request.user, 'login', ''),
            )
            payload = Formulario2AArchivoSerializer(created).data
        except Formulario2AArchivoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el archivo del formulario EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class Formulario2AArchivoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, formulario_2a_id, archivo_id):
        if formulario_2a_id < 1 or formulario_2a_id > _FORMULARIO_2A_ID_MAX:
            return Response(
                {'error': 'El campo formulario_2a_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if archivo_id < 1 or archivo_id > _ARCHIVO_ID_MAX:
            return Response(
                {'error': 'El campo archivo_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Formulario2AArchivoService.delete(formulario_2a_id, archivo_id)
        except Formulario2AArchivoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo eliminar el archivo del formulario EDAN 2A'},
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
