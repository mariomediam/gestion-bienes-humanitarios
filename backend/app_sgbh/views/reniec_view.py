from app_sgbh.services.reniec import ReniecError, consultar_por_dni
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class ReniecConsultarView(APIView):
    """
    GET /api/lf-itse/reniec/consultar/?dni=<DNI>

    Consulta los datos de una persona en RENIEC a través de la
    plataforma PIDE.

    Parámetros de query string
    --------------------------
    dni : str  (obligatorio)
        Número de DNI a consultar (8 dígitos numéricos).

    Requiere autenticación JWT.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        dni = request.query_params.get('dni', '').strip()

        if not dni:
            return Response(
                {'error': "El parámetro 'dni' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resultado = consultar_por_dni(dni)
            return Response(resultado, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ReniecError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
