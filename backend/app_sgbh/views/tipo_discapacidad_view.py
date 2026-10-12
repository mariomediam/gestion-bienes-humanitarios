from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_formulario_tipo_discapacidad,
    parse_esta_activo,
    parse_nombre_tipo_discapacidad,
    parse_tipo_discapacidad_id,
)
from app_sgbh.serializers import TipoDiscapacidadSerializer
from app_sgbh.services.tipo_discapacidad import TipoDiscapacidadService


class TipoDiscapacidadListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipo_discapacidad_id, error = parse_tipo_discapacidad_id(
            request.query_params.get('tipo_discapacidad_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo_formulario, error = parse_codigo_formulario_tipo_discapacidad(
            request.query_params.get('codigo_formulario')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_tipo_discapacidad(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = TipoDiscapacidadService.list(
                tipo_discapacidad_id=tipo_discapacidad_id,
                codigo_formulario=codigo_formulario,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = TipoDiscapacidadSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de tipos de discapacidad'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
