from rest_framework import serializers


class StockActualSerializer(serializers.Serializer):
    """Confirmed stock joined with the good, its category and its unit.

    Category and unit names come from S43cat_bah_categorias_bienes and
    S43cat_bah_unidades_medida. The remaining good columns come from
    S43cat_bah_bienes. stock_actual comes from S43vw_stock_actual.
    """

    bien_id = serializers.IntegerField()
    categoria_bien_id = serializers.IntegerField(source='bien.categoria_bien_id')
    unidad_medida_id = serializers.IntegerField(source='bien.unidad_medida_id')
    codigo = serializers.CharField(source='bien.codigo')
    nombre = serializers.CharField(source='bien.nombre')
    descripcion = serializers.CharField(source='bien.descripcion', allow_null=True)
    orden_impresion = serializers.IntegerField(
        source='bien.orden_impresion',
        allow_null=True,
    )
    esta_activo = serializers.BooleanField(source='bien.esta_activo')
    visible_planilla = serializers.BooleanField(source='bien.visible_planilla')
    stock_actual = serializers.DecimalField(max_digits=18, decimal_places=6)
    categoria_bien_nombre = serializers.CharField(
        source='bien.categoria_bien.nombre',
    )
    unidad_medida_nombre = serializers.CharField(source='bien.unidad_medida.nombre')
