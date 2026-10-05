from rest_framework import serializers

from ..models import Distrito


class DistritoSerializer(serializers.ModelSerializer):
    """Rows returned from the DISTRITO view."""

    class Meta:
        model = Distrito
        fields = (
            'departamento_id',
            'provincia_id',
            'distrito_id',
            'distrito_nombre',
            'f_activo',
        )
