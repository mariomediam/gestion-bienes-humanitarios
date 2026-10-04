from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_estado_planilla_id
from app_sgbh.serializers import PlanillaEntregaTotalSerializer
from app_sgbh.services.planilla_entrega import PlanillaEntregaService


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
