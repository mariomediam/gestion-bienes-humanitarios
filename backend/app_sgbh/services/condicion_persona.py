from ..models import CondicionPersona
from ..text_search import filter_text_like


class CondicionPersonaService:
    @staticmethod
    def list(
        condicion_persona_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_condiciones_persona ordered by condicion_persona_id.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = CondicionPersona.objects.all()
        if condicion_persona_id is not None:
            queryset = queryset.filter(condicion_persona_id=condicion_persona_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('condicion_persona_id')
