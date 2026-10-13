from rest_framework import serializers

from ..models import TipoDocumento


class TipoDocumentoSerializer(serializers.ModelSerializer):
    """Rows returned from S43cat_tipos_documento."""

    class Meta:
        model = TipoDocumento
        fields = (
            'tipo_documento_id',
            'codigo',
            'nombre',
            'esta_activo',
        )
