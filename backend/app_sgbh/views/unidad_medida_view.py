from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_abreviatura_unidad_medida,
    parse_codigo_unidad_medida,
    parse_esta_activo,
    parse_nombre_unidad_medida,
    parse_unidad_medida_id,
)
from app_sgbh.serializers import UnidadMedidaSerializer
from app_sgbh.services.unidad_medida import UnidadMedidaService


class UnidadMedidaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unidad_medida_id, error = parse_unidad_medida_id(
            request.query_params.get('unidad_medida_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_unidad_medida(request.query_params.get('codigo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_unidad_medida(request.query_params.get('nombre'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        abreviatura, error = parse_abreviatura_unidad_medida(
            request.query_params.get('abreviatura')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = UnidadMedidaService.list(
                unidad_medida_id=unidad_medida_id,
                codigo=codigo,
                nombre=nombre,
                abreviatura=abreviatura,
                esta_activo=esta_activo,
            )
            payload = UnidadMedidaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de unidades de medida'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
