from rest_framework import serializers

from ..models import StockActual


class StockActualSerializer(serializers.ModelSerializer):
    """Rows returned from S43vw_stock_actual."""

    bien_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockActual
        fields = (
            'bien_id',
            'stock_actual',
        )
