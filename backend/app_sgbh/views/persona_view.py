from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_nombre_completo,
    parse_numero_documento,
    parse_persona_id,
    parse_tipo_documento_id,
)
from app_sgbh.serializers import (
    PersonaBusquedaSerializer,
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


class PersonaBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parsed, error = _parse_busqueda(request.query_params)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = PersonaService.search(**parsed)
            payload = PersonaBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de personas'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _parse_busqueda(params):
    """Parse optional persona search filters.

    Returns (values, error_message). values is None when a filter is invalid.
    """
    parsers = (
        ('persona_id', parse_persona_id),
        ('tipo_documento_id', parse_tipo_documento_id),
        ('numero_documento', parse_numero_documento),
        ('nombre_completo', parse_nombre_completo),
    )
    values = {}
    for name, parser in parsers:
        value, error = parser(params.get(name))
        if error:
            return None, error
        values[name] = value

    return values, None


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

    def delete(self, request, persona_id):
        if persona_id < 1 or persona_id > _PERSONA_ID_MAX:
            return Response(
                {'error': 'El campo persona_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            PersonaService.delete(persona_id)
        except PersonaServiceError as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo eliminar la persona'},
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
