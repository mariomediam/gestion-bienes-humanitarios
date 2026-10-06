from rest_framework import serializers

from ..models import TipoUsoInstalacion


class TipoUsoInstalacionSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_tipos_uso_instalacion."""

    class Meta:
        model = TipoUsoInstalacion
        fields = ('tipo_uso_instalacion_id', 'codigo', 'nombre', 'esta_activo')
