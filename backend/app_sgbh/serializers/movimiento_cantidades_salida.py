from rest_framework import serializers


class MovimientoCantidadesSalidaSerializer(serializers.Serializer):
    """One salida line with the entradas already posted for the same good.

    bien_nombre comes from S43cat_bah_bienes.nombre. abreviatura_nombre
    comes from S43cat_bah_unidades_medida.abreviatura. cantidad_origen is
    the absolute quantity of the salida line. cantidad_entrada is the sum
    of absolute quantities returned for that good, or 0.
    """

    bien_id = serializers.IntegerField()
    bien_nombre = serializers.CharField()
    abreviatura_nombre = serializers.CharField(allow_null=True)
    cantidad_origen = serializers.DecimalField(max_digits=18, decimal_places=6)
    cantidad_entrada = serializers.DecimalField(max_digits=18, decimal_places=6)
