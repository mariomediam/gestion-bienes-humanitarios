from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_grado_lesion,
    parse_esta_activo,
    parse_grado_lesion_id,
    parse_nombre_grado_lesion,
)
from app_sgbh.serializers import GradoLesionSerializer
from app_sgbh.services.grado_lesion import GradoLesionService


class GradoLesionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        grado_lesion_id, error = parse_grado_lesion_id(
            request.query_params.get('grado_lesion_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_grado_lesion(request.query_params.get('codigo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_grado_lesion(request.query_params.get('nombre'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = GradoLesionService.list(
                grado_lesion_id=grado_lesion_id,
                codigo=codigo,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = GradoLesionSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de grados de lesión'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
