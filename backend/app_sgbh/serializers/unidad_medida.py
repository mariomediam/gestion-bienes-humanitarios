from rest_framework import serializers

from ..models import UnidadMedida


class UnidadMedidaSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_bah_unidades_medida."""

    class Meta:
        model = UnidadMedida
        fields = (
            'unidad_medida_id',
            'codigo',
            'nombre',
            'abreviatura',
            'esta_activo',
        )
