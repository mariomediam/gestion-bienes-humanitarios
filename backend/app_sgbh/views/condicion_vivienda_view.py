from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_condicion_vivienda,
    parse_condicion_vivienda_id,
    parse_esta_activo,
    parse_nombre_condicion_vivienda,
)
from app_sgbh.serializers import CondicionViviendaSerializer
from app_sgbh.services.condicion_vivienda import CondicionViviendaService


class CondicionViviendaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        condicion_vivienda_id, error = parse_condicion_vivienda_id(
            request.query_params.get('condicion_vivienda_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_condicion_vivienda(
            request.query_params.get('codigo')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_condicion_vivienda(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = CondicionViviendaService.list(
                condicion_vivienda_id=condicion_vivienda_id,
                codigo=codigo,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = CondicionViviendaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {
                    'error': (
                        'No se pudo obtener el catálogo de condiciones de vivienda'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
