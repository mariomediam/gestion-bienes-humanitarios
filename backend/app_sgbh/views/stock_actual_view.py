from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_bien_id
from app_sgbh.serializers import StockActualSerializer
from app_sgbh.services.stock_actual import StockActualService


class StockActualListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bien_id, error = parse_bien_id(request.query_params.get('bien_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = StockActualService.list(bien_id=bien_id)
            payload = StockActualSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el stock actual'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
