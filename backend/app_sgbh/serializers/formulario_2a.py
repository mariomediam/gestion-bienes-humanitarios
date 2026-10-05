from rest_framework import serializers


class Formulario2AUbicacionSerializer(serializers.Serializer):
    """Location fields of a Formulario 2A nested in an emergency."""

    distrito_nombre = serializers.CharField(allow_null=True)
    localidad = serializers.CharField(allow_null=True)
    barrio_sector_urbanizacion = serializers.CharField(allow_null=True)
    centro_poblado = serializers.CharField(allow_null=True)
    caserio = serializers.CharField(allow_null=True)
    anexo = serializers.CharField(allow_null=True)
    calle_manzana = serializers.CharField(allow_null=True)
    edificio_piso_dpto = serializers.CharField(allow_null=True)
    otros_ubicacion = serializers.CharField(allow_null=True)


class Formulario2ATotalSerializer(serializers.Serializer):
    """Count of rows in S43edan_formulario_2a."""

    total = serializers.IntegerField(min_value=0)


class Formulario2AViviendaBusquedaSerializer(serializers.Serializer):
    """Vivienda fields nested in a Formulario 2A search row."""

    vivienda_id = serializers.IntegerField()
    numero_lote = serializers.CharField(allow_null=True)


class Formulario2ABusquedaSerializer(serializers.Serializer):
    """One Formulario 2A row returned by the search endpoint.

    Viviendas are nested so the response has one object per formulario_2a_id.
    """

    formulario_2a_id = serializers.IntegerField()
    emergencia_id = serializers.IntegerField()
    departamento_id = serializers.CharField()
    provincia_id = serializers.CharField()
    distrito_id = serializers.CharField()
    fecha_empadronamiento = serializers.DateField()
    hora_empadronamiento = serializers.TimeField(allow_null=True)
    localidad = serializers.CharField(allow_null=True)
    barrio_sector_urbanizacion = serializers.CharField(allow_null=True)
    centro_poblado = serializers.CharField(allow_null=True)
    caserio = serializers.CharField(allow_null=True)
    anexo = serializers.CharField(allow_null=True)
    calle_manzana = serializers.CharField(allow_null=True)
    edificio_piso_dpto = serializers.CharField(allow_null=True)
    otros_ubicacion = serializers.CharField(allow_null=True)
    numero_hoja = serializers.IntegerField()
    total_hojas = serializers.IntegerField(allow_null=True)
    institucion = serializers.CharField(allow_null=True)
    evaluador_id = serializers.IntegerField()
    estado_registro_id = serializers.IntegerField()
    c_usuari_login = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_modificacion = serializers.DateTimeField(allow_null=True)
    codigo_sinpad = serializers.CharField(
        source='emergencia.codigo_sinpad',
        allow_null=True,
    )
    tipo_peligro_id = serializers.IntegerField(source='emergencia.tipo_peligro_id')
    nombre_tipo_peligro = serializers.CharField(source='emergencia.tipo_peligro.nombre')
    distrito_nombre = serializers.CharField(allow_null=True)
    evaluador_nombre = serializers.SerializerMethodField()
    viviendas = Formulario2AViviendaBusquedaSerializer(many=True)

    def get_evaluador_nombre(self, obj):
        personal = obj.evaluador
        return (
            f'{personal.apellido_paterno} {personal.apellido_materno} {personal.nombres}'
        )
