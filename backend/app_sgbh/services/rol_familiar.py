from ..models import RolFamiliar
from ..text_search import filter_text_like


class RolFamiliarService:
    @staticmethod
    def list(
        rol_familiar_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_roles_familiares ordered by rol_familiar_id.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = RolFamiliar.objects.all()
        if rol_familiar_id is not None:
            queryset = queryset.filter(rol_familiar_id=rol_familiar_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('rol_familiar_id')
