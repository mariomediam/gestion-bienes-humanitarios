from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_condicion_persona_id
from app_sgbh.serializers import Formulario2AIntegranteTotalSerializer
from app_sgbh.services.formulario_2a_integrante import Formulario2AIntegranteService


class Formulario2AIntegranteTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        condicion_persona_id, error = parse_condicion_persona_id(
            request.query_params.get('condicion_persona_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = Formulario2AIntegranteService.count(
                condicion_persona_id=condicion_persona_id
            )
            payload = Formulario2AIntegranteTotalSerializer({'total': total}).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de integrantes'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
