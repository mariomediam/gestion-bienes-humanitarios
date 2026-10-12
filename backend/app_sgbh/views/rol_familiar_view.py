from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_rol_familiar,
    parse_esta_activo,
    parse_nombre_rol_familiar,
    parse_rol_familiar_id,
)
from app_sgbh.serializers import RolFamiliarSerializer
from app_sgbh.services.rol_familiar import RolFamiliarService


class RolFamiliarListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rol_familiar_id, error = parse_rol_familiar_id(
            request.query_params.get('rol_familiar_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo, error = parse_codigo_rol_familiar(request.query_params.get('codigo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_rol_familiar(request.query_params.get('nombre'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = RolFamiliarService.list(
                rol_familiar_id=rol_familiar_id,
                codigo=codigo,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = RolFamiliarSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de roles familiares'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
