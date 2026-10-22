from ..models import StockActual


class StockActualService:
    @staticmethod
    def list(bien_id=None):
        """List rows from S43vw_stock_actual ordered by bien_id.

        The bien_id filter is optional. When it is omitted, every good
        with confirmed stock is returned.
        """
        queryset = StockActual.objects.all()
        if bien_id is not None:
            queryset = queryset.filter(bien_id=bien_id)

        return queryset.order_by('bien_id')
