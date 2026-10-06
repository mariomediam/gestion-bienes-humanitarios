from rest_framework import serializers

from ..models import MaterialPiso


class MaterialPisoSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_materiales_piso."""

    class Meta:
        model = MaterialPiso
        fields = (
            'material_piso_id',
            'codigo_formulario',
            'nombre',
            'esta_activo',
        )
