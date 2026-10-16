from ..models import CategoriaBien
from ..text_search import filter_text_like


class CategoriaBienService:
    @staticmethod
    def list(
        categoria_bien_id=None,
        codigo=None,
        nombre=None,
        orden=None,
        esta_activo=None,
    ):
        """List rows from S43cat_bah_categorias_bienes ordered by orden.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = CategoriaBien.objects.all()
        if categoria_bien_id is not None:
            queryset = queryset.filter(categoria_bien_id=categoria_bien_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if orden is not None:
            queryset = queryset.filter(orden=orden)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('orden')
