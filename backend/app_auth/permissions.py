from rest_framework.permissions import BasePermission

from app_auth.db_service import get_user_menu_access


class RequiereMenu(BasePermission):
    message = 'No tiene acceso a esta operación'

    OPERACION_POR_METODO = {
        'POST': 'nuevo',
        'PUT': 'modificar',
        'PATCH': 'modificar',
        'DELETE': 'eliminar',
    }

    def has_permission(self, request, view):
        men_codi = getattr(view, 'menu_codigo', None)
        if not men_codi:
            return False

        acceso = get_user_menu_access(request.user.login, men_codi)
        if acceso is None:
            return False

        operacion = getattr(view, 'menu_operacion', None)
        if operacion is None and request.method != 'GET':
            operacion = self.OPERACION_POR_METODO.get(request.method)

        if not operacion:
            return True
        return bool(acceso.get(operacion))