from ..models import CondicionVivienda
from ..text_search import filter_text_like


class CondicionViviendaService:
    @staticmethod
    def list(
        condicion_vivienda_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_condiciones_vivienda ordered by nombre.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = CondicionVivienda.objects.all()
        if condicion_vivienda_id is not None:
            queryset = queryset.filter(
                condicion_vivienda_id=condicion_vivienda_id
            )
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('nombre')
