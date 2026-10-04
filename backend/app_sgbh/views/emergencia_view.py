from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_esta_activo
from app_sgbh.services.emergencia import EmergenciaService


class EmergenciaTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = EmergenciaService.count(esta_activo=esta_activo)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de emergencias'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({'total': total}, status=status.HTTP_200_OK)


class EmergenciaTotalPorTipoPeligroView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = EmergenciaService.count_by_tipo_peligro(esta_activo=esta_activo)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de emergencias por tipo de peligro'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(rows, status=status.HTTP_200_OK)
