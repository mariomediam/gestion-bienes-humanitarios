from rest_framework import serializers


class AlmacenKardexBusquedaSerializer(serializers.Serializer):
    """One S43vw_alm_kardex row returned by the search endpoint.

    tipo_movimiento is the type name and estado_movimiento is the state code.
    """

    movimiento_id = serializers.IntegerField()
    almacen_id = serializers.IntegerField()
    fecha_movimiento = serializers.DateTimeField()
    tipo_movimiento_id = serializers.IntegerField()
    tipo_movimiento_codigo = serializers.CharField()
    tipo_movimiento = serializers.CharField()
    naturaleza = serializers.CharField()
    estado_movimiento = serializers.CharField()
    movimiento_origen_id = serializers.IntegerField(allow_null=True)
    documento_referencia = serializers.CharField(allow_null=True)
    movimiento_detalle_id = serializers.IntegerField()
    bien_id = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=18, decimal_places=6)
    cantidad_texto = serializers.CharField(allow_null=True)
    es_devolvible = serializers.BooleanField()
    detalle_observacion = serializers.CharField(allow_null=True)
    movimiento_observacion = serializers.CharField(allow_null=True)
