from rest_framework import serializers

from ..models import TipoPeligro


class TipoPeligroSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_tipos_peligro."""

    class Meta:
        model = TipoPeligro
        fields = ('tipo_peligro_id', 'codigo', 'nombre', 'esta_activo')
