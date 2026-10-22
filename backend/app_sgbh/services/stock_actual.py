from ..models import StockActual


class StockActualService:
    @staticmethod
    def list(bien_id=None):
        """List confirmed stock with the good, its category and its unit.

        Starts from S43vw_stock_actual and joins S43cat_bah_bienes,
        S43cat_bah_categorias_bienes and S43cat_bah_unidades_medida.
        The bien_id filter is optional. When it is omitted, every good
        with confirmed stock is returned. Ordered by bien_id. The
        queryset is ready for StockActualSerializer.
        """
        queryset = StockActual.objects.select_related(
            'bien',
            'bien__categoria_bien',
            'bien__unidad_medida',
        )
        if bien_id is not None:
            queryset = queryset.filter(bien_id=bien_id)

        return queryset.order_by('bien_id')
