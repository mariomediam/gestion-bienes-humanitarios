from rest_framework import serializers

_INT_MIN = -2147483648
_INT_MAX = 2147483647
_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


class OptionalBooleanField(serializers.BooleanField):
    """Boolean field that stores a blank value as null."""

    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('allow_null', True)
        kwargs.setdefault('default', None)
        super().__init__(**kwargs)

    def run_validation(self, data=serializers.empty):
        if data == '' or (isinstance(data, str) and data.strip() == ''):
            return None
        return super().run_validation(data)


def _id_field(name, *, required, smallint=True):
    """Integer foreign key with the Spanish messages used by the API."""
    obligatorio = f'El campo {name} es obligatorio'
    invalido = f'El campo {name} debe ser un número entero'
    messages = {
        'invalid': invalido,
        'min_value': invalido,
        'max_value': invalido,
    }
    kwargs = {
        'min_value': _SMALLINT_MIN if smallint else _INT_MIN,
        'max_value': _SMALLINT_MAX if smallint else _INT_MAX,
        'error_messages': messages,
    }
    if required:
        messages['required'] = obligatorio
        messages['null'] = obligatorio
    else:
        kwargs['required'] = False
        kwargs['allow_null'] = True
        kwargs['default'] = None
    return serializers.IntegerField(**kwargs)


class ViviendaCreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43edan_formulario_2a_viviendas.

    numero_orden is assigned by Formulario2AViviendaService for the parent
    form. Foreign keys and the parent form lock are checked there.
    fecha_creacion uses the column default.
    """

    formulario_2a_id = _id_field('formulario_2a_id', required=True, smallint=False)
    numero_lote = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo numero_lote es obligatorio',
            'blank': 'El campo numero_lote es obligatorio',
            'null': 'El campo numero_lote es obligatorio',
            'invalid': 'El campo numero_lote debe ser texto',
            'max_length': 'El campo numero_lote no debe superar 50 caracteres',
        },
    )
    tenencia_propia = OptionalBooleanField(
        error_messages={
            'invalid': 'El campo tenencia_propia debe ser 1, 0, true o false',
        },
    )
    tipo_uso_instalacion_id = _id_field('tipo_uso_instalacion_id', required=True)
    condicion_vivienda_id = _id_field('condicion_vivienda_id', required=False)
    material_techo_id = _id_field('material_techo_id', required=False)
    material_pared_id = _id_field('material_pared_id', required=False)
    material_piso_id = _id_field('material_piso_id', required=False)


class ViviendaUpdateSerializer(ViviendaCreateSerializer):
    """Validate the body used to update S43edan_formulario_2a_viviendas.

    Same fields as create, except formulario_2a_id. That column stays as
    stored, the same as numero_orden and fecha_creacion.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('formulario_2a_id', None)


class ViviendaBusquedaSerializer(serializers.Serializer):
    """One vivienda row returned after creating or updating it.

    Catalog names come from the related rows. A null foreign key yields
    a null name.
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


class ViviendaBuscarSerializer(serializers.Serializer):
    """One vivienda row returned by the search endpoint.

    Catalog names, the parent formulario, the emergency and the hazard
    come from the related rows. distrito_nombre is annotated from DISTRITO.
    A null foreign key or a missing district yields null.
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
    emergencia_id = serializers.IntegerField(source='formulario_2a.emergencia_id')
    fecha_empadronamiento = serializers.DateField(
        source='formulario_2a.fecha_empadronamiento',
    )
    hora_empadronamiento = serializers.TimeField(
        source='formulario_2a.hora_empadronamiento',
        allow_null=True,
    )
    localidad = serializers.CharField(
        source='formulario_2a.localidad',
        allow_null=True,
    )
    barrio_sector_urbanizacion = serializers.CharField(
        source='formulario_2a.barrio_sector_urbanizacion',
        allow_null=True,
    )
    centro_poblado = serializers.CharField(
        source='formulario_2a.centro_poblado',
        allow_null=True,
    )
    caserio = serializers.CharField(source='formulario_2a.caserio', allow_null=True)
    anexo = serializers.CharField(source='formulario_2a.anexo', allow_null=True)
    calle_manzana = serializers.CharField(
        source='formulario_2a.calle_manzana',
        allow_null=True,
    )
    edificio_piso_dpto = serializers.CharField(
        source='formulario_2a.edificio_piso_dpto',
        allow_null=True,
    )
    otros_ubicacion = serializers.CharField(
        source='formulario_2a.otros_ubicacion',
        allow_null=True,
    )
    numero_hoja = serializers.IntegerField(source='formulario_2a.numero_hoja')
    total_hojas = serializers.IntegerField(
        source='formulario_2a.total_hojas',
        allow_null=True,
    )
    institucion = serializers.CharField(
        source='formulario_2a.institucion',
        allow_null=True,
    )
    evaluador_id = serializers.IntegerField(source='formulario_2a.evaluador_id')
    estado_registro_id = serializers.IntegerField(
        source='formulario_2a.estado_registro_id',
    )
    codigo_sinpad = serializers.CharField(
        source='formulario_2a.emergencia.codigo_sinpad',
        allow_null=True,
    )
    tipo_peligro_id = serializers.IntegerField(
        source='formulario_2a.emergencia.tipo_peligro_id',
    )
    nombre_tipo_peligro = serializers.CharField(
        source='formulario_2a.emergencia.tipo_peligro.nombre',
    )
    distrito_nombre = serializers.CharField(allow_null=True)

    def get_condicion_vivienda_nombre(self, obj):
        return _catalog_nombre(obj.condicion_vivienda)

    def get_material_techo_nombre(self, obj):
        return _catalog_nombre(obj.material_techo)

    def get_material_pared_nombre(self, obj):
        return _catalog_nombre(obj.material_pared)

    def get_material_piso_nombre(self, obj):
        return _catalog_nombre(obj.material_piso)
