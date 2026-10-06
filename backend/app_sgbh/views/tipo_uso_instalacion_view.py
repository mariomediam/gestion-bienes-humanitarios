from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_tipo_uso_instalacion,
    parse_esta_activo,
    parse_nombre_tipo_uso_instalacion,
    parse_tipo_uso_instalacion_id,
)
from app_sgbh.serializers import TipoUsoInstalacionSerializer
from app_sgbh.services.tipo_uso_instalacion import TipoUsoInstalacionService


class TipoUsoInstalacionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_uso_instalacion_id, error = parse_tipo_uso_instalacion_id(
            request.query_params.get('tipo_uso_instalacion_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_tipo_uso_instalacion(
            request.query_params.get('codigo')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_tipo_uso_instalacion(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = TipoUsoInstalacionService.list(
                tipo_uso_instalacion_id=tipo_uso_instalacion_id,
                codigo=codigo,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = TipoUsoInstalacionSerializer(rows, many=True).data
        except Exception:
            return Response(
                {
                    'error': (
                        'No se pudo obtener el catálogo de tipos de uso de instalación'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
