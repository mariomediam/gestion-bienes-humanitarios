from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_categoria_medio_vida_id,
    parse_codigo_categoria_medio_vida,
    parse_esta_activo,
    parse_nombre_categoria_medio_vida,
)
from app_sgbh.serializers import CategoriaMedioVidaSerializer
from app_sgbh.services.categoria_medio_vida import CategoriaMedioVidaService


class CategoriaMedioVidaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categoria_medio_vida_id, error = parse_categoria_medio_vida_id(
            request.query_params.get('categoria_medio_vida_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_categoria_medio_vida(
            request.query_params.get('codigo')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_categoria_medio_vida(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = CategoriaMedioVidaService.list(
                categoria_medio_vida_id=categoria_medio_vida_id,
                codigo=codigo,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = CategoriaMedioVidaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {
                    'error': (
                        'No se pudo obtener el catálogo de categorías '
                        'de medios de vida'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
