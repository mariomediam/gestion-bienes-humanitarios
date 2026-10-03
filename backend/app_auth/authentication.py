"""
Custom JWT authentication that doesn't require Django's User model.
Validates the token and returns a lightweight user object from claims.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class ExternalUser:
    """Lightweight user object constructed from JWT claims."""

    def __init__(self, login, nombre):
        self.login = login
        self.nombre = nombre
        self.is_authenticated = True
        self.is_active = True

    @property
    def pk(self):
        return self.login

    def __str__(self):
        return self.login


class CustomJWTAuthentication(JWTAuthentication):
    """
    JWT authentication that reads user info from token claims
    instead of querying Django's auth_user table.
    """

    def get_user(self, validated_token):
        user_login = validated_token.get('user_login')
        user_name = validated_token.get('user_name', '')

        if not user_login:
            raise InvalidToken('Token no contiene información del usuario')

        return ExternalUser(login=user_login, nombre=user_name)
