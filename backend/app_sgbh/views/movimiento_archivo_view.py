from uuid import UUID

from django.http import FileResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_archivo_id,
    parse_esta_activo,
    parse_movimiento_id,
)
from app_sgbh.serializers import (
    MovimientoArchivoBusquedaSerializer,
    MovimientoArchivoSerializer,
)
from app_sgbh.services.movimiento_archivo import (
    MovimientoArchivoService,
    MovimientoArchivoServiceError,
)

_MOVIMIENTO_ID_MAX = 2147483647
_CAMPOS_DEL_SISTEMA = (
    'archivo_id',
    'movimiento_id',
    'nombre_original',
    'nombre_archivo',
    'ruta_archivo',
    'extension',
    'tamano_bytes',
    'esta_activo',
    'fecha_registro',
    'c_usuari_login',
)


class MovimientoArchivoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movimiento_id):
        if movimiento_id < 1 or movimiento_id > _MOVIMIENTO_ID_MAX:
            return Response(
                {'error': 'El campo movimiento_id debe ser un número entero'},
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
            created = MovimientoArchivoService.create(
                movimiento_id=movimiento_id,
                archivo=archivos[0],
                c_usuari_login=getattr(request.user, 'login', ''),
            )
            payload = MovimientoArchivoSerializer(created).data
        except MovimientoArchivoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar el archivo del movimiento de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class MovimientoArchivoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, movimiento_id, archivo_id):
        if movimiento_id < 1 or movimiento_id > _MOVIMIENTO_ID_MAX:
            return Response(
                {'error': 'El campo movimiento_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        archivo_uuid = _parse_archivo_id(archivo_id)
        if archivo_uuid is None:
            return Response(
                {'error': 'El campo archivo_id debe ser un UUID'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            MovimientoArchivoService.delete(movimiento_id, archivo_uuid)
        except MovimientoArchivoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo eliminar el archivo del movimiento de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MovimientoArchivoDescargarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movimiento_id, archivo_id):
        if movimiento_id < 1 or movimiento_id > _MOVIMIENTO_ID_MAX:
            return Response(
                {'error': 'El campo movimiento_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        archivo_uuid = _parse_archivo_id(archivo_id)
        if archivo_uuid is None:
            return Response(
                {'error': 'El campo archivo_id debe ser un UUID'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            descarga = MovimientoArchivoService.download(
                movimiento_id,
                archivo_uuid,
            )
            handle = descarga.path.open('rb')
        except MovimientoArchivoServiceError as exc:
            return _respuesta_error_servicio(exc)
        except OSError:
            return Response(
                {'error': 'El archivo indicado no existe'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {'error': 'No se pudo descargar el archivo del movimiento de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            response = FileResponse(
                handle,
                as_attachment=True,
                filename=descarga.filename,
                content_type=descarga.content_type,
            )
        except Exception:
            handle.close()
            return Response(
                {'error': 'No se pudo descargar el archivo del movimiento de almacén'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'private, no-store'
        return response


class MovimientoArchivoBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        archivo_id, error = parse_archivo_id(request.query_params.get('archivo_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        movimiento_id, error = parse_movimiento_id(
            request.query_params.get('movimiento_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = MovimientoArchivoService.search(
                archivo_id=archivo_id,
                movimiento_id=movimiento_id,
                esta_activo=esta_activo,
            )
            payload = MovimientoArchivoBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {
                    'error': (
                        'No se pudo obtener la búsqueda de archivos '
                        'del movimiento de almacén'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_archivo_id(archivo_id):
    if isinstance(archivo_id, UUID):
        return archivo_id
    if isinstance(archivo_id, str):
        try:
            return UUID(archivo_id)
        except ValueError:
            return None
    return None


def _respuesta_error_servicio(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    elif exc.conflict:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)
