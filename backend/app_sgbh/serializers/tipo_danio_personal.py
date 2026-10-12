from rest_framework import serializers

from ..models import TipoDanioPersonal


class TipoDanioPersonalSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_tipos_danio_personal."""

    class Meta:
        model = TipoDanioPersonal
        fields = ('tipo_danio_personal_id', 'codigo', 'nombre', 'esta_activo')
