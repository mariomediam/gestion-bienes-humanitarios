from rest_framework import serializers

from ..models import TipoDiscapacidad


class TipoDiscapacidadSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_tipos_discapacidad."""

    class Meta:
        model = TipoDiscapacidad
        fields = (
            'tipo_discapacidad_id',
            'codigo_formulario',
            'nombre',
            'esta_activo',
        )
