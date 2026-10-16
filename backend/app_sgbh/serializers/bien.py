from rest_framework import serializers


class BienBusquedaSerializer(serializers.Serializer):
    """Rows returned by the bienes search endpoint.

    Category and unit columns come from the joins with
    S43cat_bah_categorias_bienes and S43cat_bah_unidades_medida.
    """

    bien_id = serializers.IntegerField()
    categoria_bien_id = serializers.IntegerField()
    unidad_medida_id = serializers.IntegerField()
    codigo = serializers.CharField()
    nombre = serializers.CharField()
    descripcion = serializers.CharField(allow_null=True)
    orden_impresion = serializers.IntegerField(allow_null=True)
    esta_activo = serializers.BooleanField()
    visible_planilla = serializers.BooleanField()
    categoria_bien_codigo = serializers.CharField(source='categoria_bien.codigo')
    categoria_bien_nombre = serializers.CharField(source='categoria_bien.nombre')
    unidad_medida_codigo = serializers.CharField(source='unidad_medida.codigo')
    unidad_medida_nombre = serializers.CharField(source='unidad_medida.nombre')
    unidad_medida_abreviatura = serializers.CharField(
        source='unidad_medida.abreviatura',
        allow_null=True,
    )
