from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers.movimiento_cantidades_salida import (
    MovimientoCantidadesSalidaSerializer,
)
from app_sgbh.services.movimiento_cantidades_salida import (
    MovimientoCantidadesSalidaService,
)

_MOVIMIENTO_ID_MAX = 2147483647


class MovimientoCantidadesPorDevolverView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movimiento_id):
        if movimiento_id < 1 or movimiento_id > _MOVIMIENTO_ID_MAX:
            return Response(
                {'error': 'El campo movimiento_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            rows = MovimientoCantidadesSalidaService.list(movimiento_id)
            payload = MovimientoCantidadesSalidaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudieron obtener las cantidades de salida del movimiento'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
