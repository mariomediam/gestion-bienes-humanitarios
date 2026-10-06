from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_formulario_material_piso,
    parse_esta_activo,
    parse_material_piso_id,
    parse_nombre_material_piso,
)
from app_sgbh.serializers import MaterialPisoSerializer
from app_sgbh.services.material_piso import MaterialPisoService


class MaterialPisoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        material_piso_id, error = parse_material_piso_id(
            request.query_params.get('material_piso_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo_formulario, error = parse_codigo_formulario_material_piso(
            request.query_params.get('codigo_formulario')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_material_piso(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = MaterialPisoService.list(
                material_piso_id=material_piso_id,
                codigo_formulario=codigo_formulario,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = MaterialPisoSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de materiales de piso'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
