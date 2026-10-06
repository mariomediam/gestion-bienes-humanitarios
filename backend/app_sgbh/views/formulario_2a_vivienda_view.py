from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import parse_formulario_2a_id, parse_vivienda_id
from app_sgbh.serializers import ViviendaBusquedaSerializer
from app_sgbh.services.formulario_2a_vivienda import Formulario2AViviendaService


class Formulario2AViviendaBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vivienda_id, error = parse_vivienda_id(request.query_params.get('vivienda_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        formulario_2a_id, error = parse_formulario_2a_id(
            request.query_params.get('formulario_2a_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = Formulario2AViviendaService.search(
                vivienda_id=vivienda_id,
                formulario_2a_id=formulario_2a_id,
            )
            payload = ViviendaBusquedaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener la búsqueda de viviendas'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
