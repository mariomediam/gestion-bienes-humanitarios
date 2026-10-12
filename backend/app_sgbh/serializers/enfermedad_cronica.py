from rest_framework import serializers

from ..models import EnfermedadCronica


class EnfermedadCronicaSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_enfermedades_cronicas."""

    class Meta:
        model = EnfermedadCronica
        fields = (
            'enfermedad_cronica_id',
            'codigo_formulario',
            'nombre',
            'esta_activo',
        )
