from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_categoria_bien_id,
    parse_codigo_categoria_bien,
    parse_esta_activo,
    parse_nombre_categoria_bien,
    parse_orden_categoria_bien,
)
from app_sgbh.serializers import CategoriaBienSerializer
from app_sgbh.services.categoria_bien import CategoriaBienService


class CategoriaBienListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categoria_bien_id, error = parse_categoria_bien_id(
            request.query_params.get('categoria_bien_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_categoria_bien(request.query_params.get('codigo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_categoria_bien(request.query_params.get('nombre'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        orden, error = parse_orden_categoria_bien(request.query_params.get('orden'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = CategoriaBienService.list(
                categoria_bien_id=categoria_bien_id,
                codigo=codigo,
                nombre=nombre,
                orden=orden,
                esta_activo=esta_activo,
            )
            payload = CategoriaBienSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de categorías de bienes'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
