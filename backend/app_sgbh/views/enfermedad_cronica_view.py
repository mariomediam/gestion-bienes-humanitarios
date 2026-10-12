from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.query_params import (
    parse_codigo_formulario_enfermedad_cronica,
    parse_enfermedad_cronica_id,
    parse_esta_activo,
    parse_nombre_enfermedad_cronica,
)
from app_sgbh.serializers import EnfermedadCronicaSerializer
from app_sgbh.services.enfermedad_cronica import EnfermedadCronicaService


class EnfermedadCronicaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enfermedad_cronica_id, error = parse_enfermedad_cronica_id(
            request.query_params.get('enfermedad_cronica_id')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        codigo_formulario, error = parse_codigo_formulario_enfermedad_cronica(
            request.query_params.get('codigo_formulario')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        nombre, error = parse_nombre_enfermedad_cronica(
            request.query_params.get('nombre')
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        esta_activo, error = parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = EnfermedadCronicaService.list(
                enfermedad_cronica_id=enfermedad_cronica_id,
                codigo_formulario=codigo_formulario,
                nombre=nombre,
                esta_activo=esta_activo,
            )
            payload = EnfermedadCronicaSerializer(rows, many=True).data
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el catálogo de enfermedades crónicas'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(payload, status=status.HTTP_200_OK)
