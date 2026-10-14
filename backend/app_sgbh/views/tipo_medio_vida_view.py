from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_categoria_medio_vida_id,
    parse_codigo_formulario_tipo_medio_vida,
    parse_esta_activo,
    parse_nombre_tipo_medio_vida,
    parse_tipo_medio_vida_id,
)
from app_sgbh.serializers import TipoMedioVidaSerializer
from app_sgbh.services.tipo_medio_vida import TipoMedioVidaService


class TipoMedioVidaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_medio_vida_id, error = parse_tipo_medio_vida_id(
            request.query_params.get('tipo_medio_vida_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        categoria_medio_vida_id, error = parse_categoria_medio_vida_id(
            request.query_params.get('categoria_medio_vida_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo_formulario, error = parse_codigo_formulario_tipo_medio_vida(
            request.query_params.get('codigo_formulario')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_tipo_medio_vida(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = TipoMedioVidaService.list(
                tipo_medio_vida_id=tipo_medio_vida_id,
                categoria_medio_vida_id=categoria_medio_vida_id,
                codigo_formulario=codigo_formulario,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = TipoMedioVidaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de tipos de medio de vida'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
