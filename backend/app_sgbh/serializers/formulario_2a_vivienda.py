from rest_framework import serializers


class ViviendaBusquedaSerializer(serializers.Serializer):
    """One vivienda row returned by the search endpoint.

    Catalog names follow the LEFT JOIN aliases of the search query.
    A null foreign key yields a null name.
    """

    vivienda_id = serializers.IntegerField()
    formulario_2a_id = serializers.IntegerField()
    numero_orden = serializers.IntegerField()
    numero_lote = serializers.CharField(allow_null=True)
    tenencia_propia = serializers.BooleanField(allow_null=True)
    tipo_uso_instalacion_id = serializers.IntegerField()
    condicion_vivienda_id = serializers.IntegerField(allow_null=True)
    material_techo_id = serializers.IntegerField(allow_null=True)
    material_pared_id = serializers.IntegerField(allow_null=True)
    material_piso_id = serializers.IntegerField(allow_null=True)
    fecha_creacion = serializers.DateTimeField()
    tipo_uso_instalacion_nombre = serializers.CharField(
        source='tipo_uso_instalacion.nombre',
    )
    condicion_vivienda_nombre = serializers.SerializerMethodField()
    material_techo_nombre = serializers.SerializerMethodField()
    material_pared_nombre = serializers.SerializerMethodField()
    material_piso_nombre = serializers.SerializerMethodField()

    def get_condicion_vivienda_nombre(self, obj):
        return _catalog_nombre(obj.condicion_vivienda)

    def get_material_techo_nombre(self, obj):
        return _catalog_nombre(obj.material_techo)

    def get_material_pared_nombre(self, obj):
        return _catalog_nombre(obj.material_pared)

    def get_material_piso_nombre(self, obj):
        return _catalog_nombre(obj.material_piso)


def _catalog_nombre(catalog):
    if catalog is None:
        return None
    return catalog.nombre
