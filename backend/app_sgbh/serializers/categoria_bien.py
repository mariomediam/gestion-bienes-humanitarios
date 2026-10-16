from rest_framework import serializers

from ..models import CategoriaBien


class CategoriaBienSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_bah_categorias_bienes."""

    class Meta:
        model = CategoriaBien
        fields = (
            'categoria_bien_id',
            'codigo',
            'nombre',
            'orden',
            'esta_activo',
        )
