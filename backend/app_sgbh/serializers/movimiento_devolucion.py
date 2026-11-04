from rest_framework import serializers


class MovimientoDevolucionBusquedaSerializer(serializers.Serializer):
    """One DEVOLUCION row with its origin document and one detail line.

    Header, almacén, type and state columns come from S43alm_movimientos
    and its catalogs. tipo_movimiento_origen_nombre and
    documento_origen_referencia come from the origin movement. Detail, bien
    and unit columns are null when the movement has no lines.
    tipo_movimiento_requiere_origen is requiere_movimiento_origen.
    movimiento_detalle_observacion is the detail observacion.
    """

    movimiento_id = serializers.IntegerField()
    almacen_id = serializers.IntegerField()
    tipo_movimiento_id = serializers.IntegerField()
    estado_movimiento_id = serializers.IntegerField()
    movimiento_origen_id = serializers.IntegerField(allow_null=True)
    fecha_movimiento = serializers.DateTimeField()
    documento_referencia = serializers.CharField(allow_null=True)
    fecha_documento = serializers.DateField(allow_null=True)
    destinatario = serializers.CharField(allow_null=True)
    observacion = serializers.CharField(allow_null=True)
    fecha_confirmacion = serializers.DateTimeField(allow_null=True)
    encargado_almacen_id = serializers.IntegerField()
    c_usuari_login = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_modificacion = serializers.DateTimeField(allow_null=True)
    almacen_codigo = serializers.CharField(source='almacen.codigo')
    almacen_nombre = serializers.CharField(source='almacen.nombre')
    tipo_movimiento_codigo = serializers.CharField(source='tipo_movimiento.codigo')
    tipo_movimiento_nombre = serializers.CharField(source='tipo_movimiento.nombre')
    tipo_movimiento_naturaleza = serializers.CharField(
        source='tipo_movimiento.naturaleza'
    )
    tipo_movimiento_requiere_origen = serializers.BooleanField(
        source='tipo_movimiento.requiere_movimiento_origen'
    )
    estado_movimiento_codigo = serializers.CharField(source='estado_movimiento.codigo')
    estado_movimiento_nombre = serializers.CharField(source='estado_movimiento.nombre')
    tipo_movimiento_origen_nombre = serializers.CharField(allow_null=True)
    documento_origen_referencia = serializers.CharField(allow_null=True)
    movimiento_detalle_id = serializers.IntegerField(allow_null=True)
    bien_id = serializers.IntegerField(allow_null=True)
    cantidad = serializers.DecimalField(
        max_digits=18,
        decimal_places=6,
        allow_null=True,
    )
    cantidad_texto = serializers.CharField(allow_null=True)
    es_devolvible = serializers.BooleanField(allow_null=True)
    movimiento_detalle_observacion = serializers.CharField(allow_null=True)
    categoria_bien_id = serializers.IntegerField(allow_null=True)
    unidad_medida_id = serializers.IntegerField(allow_null=True)
    bien_codigo = serializers.CharField(allow_null=True)
    bien_nombre = serializers.CharField(allow_null=True)
    unidad_medida_codigo = serializers.CharField(allow_null=True)
    unidad_medida_nombre = serializers.CharField(allow_null=True)
    unidad_medida_abreviatura = serializers.CharField(allow_null=True)
