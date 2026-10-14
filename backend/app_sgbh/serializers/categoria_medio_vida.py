from rest_framework import serializers

from ..models import CategoriaMedioVida


class CategoriaMedioVidaSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_categorias_medios_vida."""

    class Meta:
        model = CategoriaMedioVida
        fields = (
            'categoria_medio_vida_id',
            'codigo',
            'nombre',
            'esta_activo',
        )
