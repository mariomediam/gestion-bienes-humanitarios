from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_sgbh.services.emergencia import EmergenciaService

_TRUE_VALUES = {'1', 'true'}
_FALSE_VALUES = {'0', 'false'}


def _parse_esta_activo(raw_value):
    """Parse the optional esta_activo query param.

    Returns (value, error_message). value is True, False or None.
    """
    if raw_value is None or raw_value == '':
        return None, None

    normalized = str(raw_value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True, None
    if normalized in _FALSE_VALUES:
        return False, None

    return None, 'El filtro esta_activo debe ser 1, 0, true o false'


class EmergenciaTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        esta_activo, error = _parse_esta_activo(request.query_params.get('esta_activo'))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total = EmergenciaService.count(esta_activo=esta_activo)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el total de emergencias'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({'total': total}, status=status.HTTP_200_OK)
