from rest_framework import serializers

from ..models import TipoMovimiento


class TipoMovimientoSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_alm_tipos_movimiento."""

    class Meta:
        model = TipoMovimiento
        fields = (
            'tipo_movimiento_id',
            'codigo',
            'nombre',
            'naturaleza',
            'requiere_movimiento_origen',
            'esta_activo',
        )
