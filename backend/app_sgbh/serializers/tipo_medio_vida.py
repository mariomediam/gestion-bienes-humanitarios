from rest_framework import serializers

from ..models import TipoMedioVida


class TipoMedioVidaSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_tipos_medios_vida."""

    categoria_medio_vida_id = serializers.IntegerField()

    class Meta:
        model = TipoMedioVida
        fields = (
            'tipo_medio_vida_id',
            'categoria_medio_vida_id',
            'codigo_formulario',
            'nombre',
            'esta_activo',
        )
