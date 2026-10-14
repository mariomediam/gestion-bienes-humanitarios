from ..models import CategoriaMedioVida
from ..text_search import filter_text_like


class CategoriaMedioVidaService:
    @staticmethod
    def list(
        categoria_medio_vida_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_categorias_medios_vida ordered by id.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = CategoriaMedioVida.objects.all()
        if categoria_medio_vida_id is not None:
            queryset = queryset.filter(
                categoria_medio_vida_id=categoria_medio_vida_id
            )
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('categoria_medio_vida_id')
