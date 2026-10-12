from rest_framework import serializers

_INT_MIN = -2147483648
_INT_MAX = 2147483647
_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


class Formulario2AIntegranteTotalSerializer(serializers.Serializer):
    """Count of rows in S43edan_formulario_2a_integrantes."""

    total = serializers.IntegerField(min_value=0)


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


class IntegranteCreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43edan_formulario_2a_integrantes.

    numero_orden is assigned by Formulario2AIntegranteService for the parent
    familia. Foreign keys and the parent form lock are checked there.
    fecha_creacion uses the column default.
    edad and gestante_semanas follow the table checks.
    """

    familia_id = _id_field('familia_id', required=True, smallint=False)
    persona_id = _id_field('persona_id', required=True, smallint=False)
    rol_familiar_id = _id_field('rol_familiar_id', required=True)
    edad = serializers.IntegerField(
        min_value=0,
        max_value=130,
        error_messages={
            'required': 'El campo edad es obligatorio',
            'null': 'El campo edad es obligatorio',
            'invalid': 'El campo edad debe ser un número entero',
            'min_value': 'El campo edad debe estar entre 0 y 130',
            'max_value': 'El campo edad debe estar entre 0 y 130',
        },
    )
    condicion_persona_id = _id_field('condicion_persona_id', required=True)
    tipo_danio_personal_id = _id_field('tipo_danio_personal_id', required=False)
    grado_lesion_id = _id_field('grado_lesion_id', required=False)
    gestante_semanas = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        min_value=1,
        max_value=45,
        error_messages={
            'invalid': 'El campo gestante_semanas debe ser un número entero',
            'min_value': 'El campo gestante_semanas debe estar entre 1 y 45',
            'max_value': 'El campo gestante_semanas debe estar entre 1 y 45',
        },
    )
    tipo_discapacidad_id = _id_field('tipo_discapacidad_id', required=False)
    enfermedad_cronica_id = _id_field('enfermedad_cronica_id', required=False)


class IntegranteUpdateSerializer(IntegranteCreateSerializer):
    """Validate the body used to update S43edan_formulario_2a_integrantes.

    Same fields as create, except familia_id. That column stays as stored,
    the same as numero_orden and fecha_creacion.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('familia_id', None)


class IntegranteBusquedaSerializer(serializers.Serializer):
    """One integrante row returned after it is created or updated.

    Catalog names follow the related rows. A null foreign key yields a null name.
    """

    integrante_id = serializers.IntegerField()
    familia_id = serializers.IntegerField()
    persona_id = serializers.IntegerField()
    rol_familiar_id = serializers.IntegerField()
    numero_orden = serializers.IntegerField()
    edad = serializers.IntegerField()
    condicion_persona_id = serializers.IntegerField()
    tipo_danio_personal_id = serializers.IntegerField(allow_null=True)
    grado_lesion_id = serializers.IntegerField(allow_null=True)
    gestante_semanas = serializers.IntegerField(allow_null=True)
    tipo_discapacidad_id = serializers.IntegerField(allow_null=True)
    enfermedad_cronica_id = serializers.IntegerField(allow_null=True)
    fecha_creacion = serializers.DateTimeField()
    rol_familiar_nombre = serializers.CharField(source='rol_familiar.nombre')
    condicion_persona_nombre = serializers.CharField(
        source='condicion_persona.nombre',
    )
    tipo_danio_personal_nombre = serializers.SerializerMethodField()
    grado_lesion_nombre = serializers.SerializerMethodField()
    tipo_discapacidad_nombre = serializers.SerializerMethodField()
    enfermedad_cronica_nombre = serializers.SerializerMethodField()

    def get_tipo_danio_personal_nombre(self, obj):
        return _catalog_nombre(obj.tipo_danio_personal)

    def get_grado_lesion_nombre(self, obj):
        return _catalog_nombre(obj.grado_lesion)

    def get_tipo_discapacidad_nombre(self, obj):
        return _catalog_nombre(obj.tipo_discapacidad)

    def get_enfermedad_cronica_nombre(self, obj):
        return _catalog_nombre(obj.enfermedad_cronica)


def _catalog_nombre(catalog):
    if catalog is None:
        return None
    return catalog.nombre
