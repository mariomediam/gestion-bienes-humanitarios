import json

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers import (
    CargaFormularios2AResultadoSerializer,
    CargaFormularios2ASerializer,
    mensaje_error_carga,
)
from app_sgbh.services.formulario_2a_carga import (
    Formulario2ACargaService,
    Formulario2ACargaServiceError,
)


class Formulario2ACargaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        datos, error = _leer_json(request)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CargaFormularios2ASerializer(data=datos)
        if not serializer.is_valid():
            return Response(
                {'error': mensaje_error_carga(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            creados = Formulario2ACargaService.cargar(
                formularios=serializer.validated_data['formularios'],
                c_usuari_login=getattr(request.user, 'login', ''),
            )
            payload = CargaFormularios2AResultadoSerializer(
                {'formularios': creados},
            ).data
        except Formulario2ACargaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudieron cargar los formularios EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


def _leer_json(request):
    """Return the JSON object from an uploaded file or from the request body."""
    archivos = request.FILES.getlist('archivo')
    if len(archivos) > 1:
        return None, 'Solo se puede cargar un archivo por solicitud'
    if len(archivos) == 1:
        return _json_de_archivo(archivos[0])

    content_type = request.content_type or ''
    if 'application/json' in content_type:
        if not isinstance(request.data, dict):
            return None, 'El archivo JSON no tiene el formato esperado'
        return request.data, None

    return None, 'El archivo JSON es obligatorio'


def _json_de_archivo(archivo):
    nombre = str(getattr(archivo, 'name', '') or '')
    if nombre and not nombre.lower().endswith('.json'):
        return None, 'El archivo debe tener extensión .json'
    try:
        texto = archivo.read().decode('utf-8-sig')
        datos = json.loads(texto)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, 'El archivo no contiene un JSON válido'
    if not isinstance(datos, dict):
        return None, 'El archivo JSON no tiene el formato esperado'
    return datos, None


def _respuesta_error_servicio(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    elif exc.conflict:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)
