from rest_framework import serializers


class MovimientoArchivoSerializer(serializers.Serializer):
    """One file row returned after it is stored.

    ruta_archivo stays out of the response because it is an internal path.
    """

    archivo_id = serializers.UUIDField()
    movimiento_id = serializers.IntegerField()
    nombre_original = serializers.CharField()
    nombre_archivo = serializers.CharField()
    extension = serializers.CharField(allow_null=True)
    tamano_bytes = serializers.IntegerField(allow_null=True)
    esta_activo = serializers.BooleanField()
    fecha_registro = serializers.DateTimeField()
    c_usuari_login = serializers.CharField()


class MovimientoArchivoBusquedaSerializer(serializers.Serializer):
    """One file row from the search.

    ruta_archivo stays out of the response because it is an internal path.
    almacen_id and documento_referencia come from the parent movement.
    documento_referencia is null when the movement has no reference.
    """

    archivo_id = serializers.UUIDField()
    movimiento_id = serializers.IntegerField()
    nombre_original = serializers.CharField()
    nombre_archivo = serializers.CharField()
    extension = serializers.CharField(allow_null=True)
    tamano_bytes = serializers.IntegerField(allow_null=True)
    esta_activo = serializers.BooleanField()
    fecha_registro = serializers.DateTimeField()
    c_usuari_login = serializers.CharField()
    almacen_id = serializers.IntegerField(source='movimiento.almacen_id')
    documento_referencia = serializers.CharField(
        source='movimiento.documento_referencia',
        allow_null=True,
    )
