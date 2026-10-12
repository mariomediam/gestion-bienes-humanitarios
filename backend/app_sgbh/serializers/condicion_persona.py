from rest_framework import serializers

from ..models import CondicionPersona


class CondicionPersonaSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_condiciones_persona."""

    class Meta:
        model = CondicionPersona
        fields = ('condicion_persona_id', 'codigo', 'nombre', 'esta_activo')
