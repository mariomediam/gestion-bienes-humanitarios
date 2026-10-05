from rest_framework import serializers

from ..models import Personal


class PersonalSerializer(serializers.ModelSerializer):
    """Rows returned from S43bah_personal."""

    class Meta:
        model = Personal
        fields = (
            'personal_id',
            'apellido_paterno',
            'apellido_materno',
            'nombres',
            'es_evaluador_edan',
            'es_encargado_almacen',
            'esta_activo',
            'fecha_creacion',
            'fecha_modificacion',
        )
