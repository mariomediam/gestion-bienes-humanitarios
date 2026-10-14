from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.serializers.formulario_2a_reporte import Formulario2AReporteSerializer
from app_sgbh.services.formulario_2a import Formulario2AServiceError
from app_sgbh.services.formulario_2a_reporte import Formulario2AReporteService

_FORMULARIO_2A_ID_MAX = 2147483647


class Formulario2AReporteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, formulario_2a_id):
        if formulario_2a_id < 1 or formulario_2a_id > _FORMULARIO_2A_ID_MAX:
            return Response(
                {'error': 'El campo formulario_2a_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reporte = Formulario2AReporteService.get(formulario_2a_id)
            payload = Formulario2AReporteSerializer(reporte).data
        except Formulario2AServiceError as exc:
            if exc.not_found:
                http_status = status.HTTP_404_NOT_FOUND
            elif exc.conflict:
                http_status = status.HTTP_409_CONFLICT
            else:
                http_status = status.HTTP_400_BAD_REQUEST
            return Response({'error': exc.message}, status=http_status)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el reporte del formulario EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
