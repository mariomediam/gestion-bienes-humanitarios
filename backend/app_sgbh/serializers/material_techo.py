from rest_framework import serializers

from ..models import MaterialTecho


class MaterialTechoSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_materiales_techo."""

    class Meta:
        model = MaterialTecho
        fields = (
            'material_techo_id',
            'codigo_formulario',
            'nombre',
            'esta_activo',
        )
