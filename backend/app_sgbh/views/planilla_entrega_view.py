from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_estado_planilla_id,
    parse_excluir_planilla_entrega_id,
)
from app_sgbh.serializers.planilla_entrega import (
    Formulario2ATienePlanillaBahSerializer,
    PlanillaEntregaCreateSerializer,
    PlanillaEntregaSerializer,
    PlanillaEntregaTotalSerializer,
)
from app_sgbh.services.formulario_2a import (
    Formulario2AService,
    Formulario2AServiceError,
)
from app_sgbh.services.movimiento import MovimientoServiceError
from app_sgbh.services.planilla_entrega import (
    PlanillaEntregaService,
    PlanillaEntregaServiceError,
    formulario_tiene_planilla_bah,
)

_FORMULARIO_2A_ID_MAX = 2147483647


class PlanillaEntregaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'El cuerpo de la solicitud no es válido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PlanillaEntregaCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': _first_error_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            created = PlanillaEntregaService.create(
                c_usuari_login=getattr(request.user, 'login', ''),
                **serializer.validated_data,
            )
            payload = PlanillaEntregaSerializer(created).data
        except (PlanillaEntregaServiceError, MovimientoServiceError) as exc:
            return _respuesta_error_servicio(exc)
        except Exception:
            return Response(
                {'error': 'No se pudo registrar la planilla BAH'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_201_CREATED)


class PlanillaEntregaTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estado_planilla_id, error = parse_estado_planilla_id(
            request.query_params.get('estado_planilla_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = PlanillaEntregaService.count(estado_planilla_id=estado_planilla_id)
            payload = PlanillaEntregaTotalSerializer({'total': total}).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de planillas BAH'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


class Formulario2ATienePlanillaBahView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, formulario_2a_id):
        if formulario_2a_id < 1 or formulario_2a_id > _FORMULARIO_2A_ID_MAX:
            return Response(
                {'error': 'El campo formulario_2a_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        excluir_planilla_entrega_id, error = parse_excluir_planilla_entrega_id(
            request.query_params.get('excluir_planilla_entrega_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Formulario2AService.get(formulario_2a_id)
            tiene_planilla_bah = formulario_tiene_planilla_bah(
                formulario_2a_id,
                excluir_planilla_entrega_id=excluir_planilla_entrega_id,
            )
            payload = Formulario2ATienePlanillaBahSerializer(
                {'tiene_planilla_bah': tiene_planilla_bah}
            ).data
        except Formulario2AServiceError as exc:
            return _respuesta_error_formulario(exc)
        except Exception:
            return Response(
                {
                    'error': (
                        'No se pudo consultar si el formulario EDAN 2A '
                        'tiene planilla BAH'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)


def _respuesta_error_formulario(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    elif exc.conflict:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)


def _respuesta_error_servicio(exc):
    if exc.not_found:
        http_status = status.HTTP_404_NOT_FOUND
    elif exc.conflict:
        http_status = status.HTTP_409_CONFLICT
    else:
        http_status = status.HTTP_400_BAD_REQUEST
    return Response({'error': exc.message}, status=http_status)


def _first_error_message(errors):
    """Return the first nested serializer error as one Spanish message."""
    if isinstance(errors, dict):
        for value in errors.values():
            message = _first_error_message(value)
            if message:
                return message
    elif isinstance(errors, (list, tuple)):
        for item in errors:
            message = _first_error_message(item)
            if message:
                return message
    elif errors:
        return str(errors)
    return 'Los datos enviados no son válidos'
