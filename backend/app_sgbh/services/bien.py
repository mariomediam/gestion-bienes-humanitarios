from ..models import Bien
from ..text_search import filter_text_like


class BienService:
    @staticmethod
    def search(
        bien_id=None,
        categoria_bien_id=None,
        unidad_medida_id=None,
        codigo=None,
        nombre=None,
    ):
        """Return S43cat_bah_bienes rows with category and unit of measure.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. With no filters, every row
        is returned. bien_id, categoria_bien_id, unidad_medida_id and codigo
        are exact. nombre uses a case-insensitive LIKE. Spaces in the text
        become '%'. Ordered by nombre. The queryset is ready for
        BienBusquedaSerializer.
        """
        queryset = Bien.objects.select_related('categoria_bien', 'unidad_medida')
        if bien_id is not None:
            queryset = queryset.filter(bien_id=bien_id)
        if categoria_bien_id is not None:
            queryset = queryset.filter(categoria_bien_id=categoria_bien_id)
        if unidad_medida_id is not None:
            queryset = queryset.filter(unidad_medida_id=unidad_medida_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)

        return queryset.order_by('nombre')
