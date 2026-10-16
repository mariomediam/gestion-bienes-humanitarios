from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_tipo_movimiento,
    parse_esta_activo,
    parse_naturaleza_tipo_movimiento,
    parse_nombre_tipo_movimiento,
    parse_requiere_movimiento_origen,
    parse_tipo_movimiento_id,
)
from app_sgbh.serializers import TipoMovimientoSerializer
from app_sgbh.services.tipo_movimiento import TipoMovimientoService


class TipoMovimientoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_movimiento_id, error = parse_tipo_movimiento_id(
            request.query_params.get('tipo_movimiento_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_tipo_movimiento(
            request.query_params.get('codigo')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_tipo_movimiento(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        naturaleza, error = parse_naturaleza_tipo_movimiento(
            request.query_params.get('naturaleza')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        requiere_movimiento_origen, error = parse_requiere_movimiento_origen(
            request.query_params.get('requiere_movimiento_origen')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = TipoMovimientoService.list(
                tipo_movimiento_id=tipo_movimiento_id,
                codigo=codigo,
                nombre=nombre,
                naturaleza=naturaleza,
                requiere_movimiento_origen=requiere_movimiento_origen,
                esta_activo=esta_activo,
            )
            payload = TipoMovimientoSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de tipos de movimiento'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
