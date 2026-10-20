from rest_framework import serializers


class PlanillaEntregaReporteBienSerializer(serializers.Serializer):
    """One printed goods line of a planilla BAH."""

    categoria_bien_nombre = serializers.CharField(allow_null=True)
    bien_nombre = serializers.CharField(allow_null=True)
    cantidad = serializers.DecimalField(
        max_digits=18,
        decimal_places=6,
        allow_null=True,
    )
    cantidad_texto = serializers.CharField(allow_null=True)


class PlanillaEntregaReporteSerializer(serializers.Serializer):
    """Printable planilla BAH: header of the sheet and one row per good."""

    movimiento_id = serializers.IntegerField(allow_null=True)
    planilla_entrega_id = serializers.IntegerField()
    numero_planilla = serializers.IntegerField()
    anio_planilla = serializers.IntegerField()
    region_nombre = serializers.CharField()
    provincia_nombre = serializers.CharField()
    distrito_nombre = serializers.CharField(allow_null=True)
    localidad = serializers.CharField(allow_null=True)
    barrio_sector_urbanizacion = serializers.CharField(allow_null=True)
    codigo_sinpad = serializers.CharField(allow_null=True)
    entregado_por_gore = serializers.CharField(allow_blank=True)
    municip_prov = serializers.CharField(allow_null=True)
    municip_dist = serializers.CharField(allow_blank=True)
    tipo_peligro_nombre = serializers.CharField(allow_null=True)
    planilla_fecha_entrega = serializers.DateField()
    direccion = serializers.CharField(allow_null=True)
    integrante_receptor_nombre = serializers.CharField(allow_null=True)
    integrante_receptor_doc_ident = serializers.CharField(allow_null=True)
    nro_integrantes_familia = serializers.IntegerField()
    encargado_almacen_nombre = serializers.CharField(allow_null=True)
    bienes = PlanillaEntregaReporteBienSerializer(many=True)
