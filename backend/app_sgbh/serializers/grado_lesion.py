from rest_framework import serializers

from ..models import GradoLesion


class GradoLesionSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_grados_lesion."""

    class Meta:
        model = GradoLesion
        fields = ('grado_lesion_id', 'codigo', 'nombre', 'esta_activo')
