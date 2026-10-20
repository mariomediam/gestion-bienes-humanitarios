from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers.planilla_entrega_reporte import (
    PlanillaEntregaReporteSerializer,
)
from app_sgbh.services.planilla_entrega import PlanillaEntregaServiceError
from app_sgbh.services.planilla_entrega_reporte import PlanillaEntregaReporteService

_PLANILLA_ENTREGA_ID_MAX = 2147483647


class PlanillaEntregaReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, planilla_entrega_id):
        if planilla_entrega_id < 1 or planilla_entrega_id > _PLANILLA_ENTREGA_ID_MAX:
            return Response(
                {'error': 'El campo planilla_entrega_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reporte = PlanillaEntregaReporteService.get(planilla_entrega_id)
            payload = PlanillaEntregaReporteSerializer(reporte).data
        except PlanillaEntregaServiceError as exc:
            if exc.not_found:
                http_status = status.HTTP_404_NOT_FOUND
            elif exc.conflict:
                http_status = status.HTTP_409_CONFLICT
            else:
                http_status = status.HTTP_400_BAD_REQUEST
            return Response({'error': exc.message}, status=http_status)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el reporte de la planilla BAH'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
