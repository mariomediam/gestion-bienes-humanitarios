from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .db_service import validate_user, get_user_menus, change_user_password


class LoginView(APIView):
    """Authenticate user via S07ValidarUsuario2 stored procedure."""

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'error': 'Usuario y contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = validate_user(username, password)
        except Exception:
            return Response(
                {'error': 'Error de conexión con el servidor de autenticación'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if result['estado'] != 'OK':
            return Response(
                {'error': result['estado']},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_login = result['login']
        user_name = result['nombre']

        # Generate JWT tokens manually
        refresh = RefreshToken()
        refresh['user_login'] = user_login
        refresh['user_name'] = user_name

        # Fetch user menus/permissions
        try:
            menus = get_user_menus(user_login)
        except Exception:
            menus = []

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'login': user_login,
                'nombre': user_name,
                'menus': menus,
            }
        }, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """Refresh an access token using a valid refresh token."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {'error': 'Token inválido o expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MeView(APIView):
    """Get current user info from JWT token claims."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.auth
        user_login = token.get('user_login', '')
        user_name = token.get('user_name', '')

        return Response({
            'login': user_login,
            'nombre': user_name,
        }, status=status.HTTP_200_OK)


class UserMenusView(APIView):
    """Get menu permissions for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_login = request.user.login

        try:
            menus = get_user_menus(user_login)
        except Exception as e:
            print(f"[ERROR] get_user_menus({user_login}): {type(e).__name__}: {e}")
            return Response(
                {'error': 'Error al obtener los menús del usuario'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response({'menus': menus}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """Change password for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_password = request.data.get('new_password', '').strip()

        if not new_password:
            return Response(
                {'error': 'La nueva contraseña es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_login = request.user.login

        try:
            change_user_password(user_login, new_password)
        except Exception as e:
            print(f"[ERROR] change_user_password({user_login}): {type(e).__name__}: {e}")
            return Response(
                {'error': 'Error al cambiar la contraseña'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {'message': 'Contraseña actualizada correctamente'},
            status=status.HTTP_200_OK
        )
