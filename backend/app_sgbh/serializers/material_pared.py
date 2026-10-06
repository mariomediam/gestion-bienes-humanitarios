from rest_framework import serializers

from ..models import MaterialPared


class MaterialParedSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_materiales_pared."""

    class Meta:
        model = MaterialPared
        fields = (
            'material_pared_id',
            'codigo_formulario',
            'nombre',
            'esta_activo',
        )
