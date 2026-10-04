from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_estado_registro_id
from app_sgbh.serializers import Formulario2ATotalSerializer
from app_sgbh.services.formulario_2a import Formulario2AService


class Formulario2ATotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estado_registro_id, error = parse_estado_registro_id(
            request.query_params.get('estado_registro_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = Formulario2AService.count(estado_registro_id=estado_registro_id)
            payload = Formulario2ATotalSerializer({'total': total}).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de formularios EDAN 2A'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
