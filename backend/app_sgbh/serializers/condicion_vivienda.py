from rest_framework import serializers

from ..models import CondicionVivienda


class CondicionViviendaSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_condiciones_vivienda."""

    class Meta:
        model = CondicionVivienda
        fields = ('condicion_vivienda_id', 'codigo', 'nombre', 'esta_activo')
