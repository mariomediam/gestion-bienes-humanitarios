from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_tipo_documento,
    parse_esta_activo,
    parse_nombre_tipo_documento,
    parse_tipo_documento_id,
)
from app_sgbh.serializers import TipoDocumentoSerializer
from app_sgbh.services.tipo_documento import TipoDocumentoService


class TipoDocumentoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_documento_id, error = parse_tipo_documento_id(
            request.query_params.get('tipo_documento_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_tipo_documento(request.query_params.get('codigo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_tipo_documento(request.query_params.get('nombre'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = TipoDocumentoService.list(
                tipo_documento_id=tipo_documento_id,
                codigo=codigo,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = TipoDocumentoSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de tipos de documento'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
