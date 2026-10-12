from rest_framework import serializers

from ..models import RolFamiliar


class RolFamiliarSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_roles_familiares."""

    class Meta:
        model = RolFamiliar
        fields = ('rol_familiar_id', 'codigo', 'nombre', 'esta_activo')
