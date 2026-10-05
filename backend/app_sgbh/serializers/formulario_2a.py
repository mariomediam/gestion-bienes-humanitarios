from rest_framework import serializers

_INT_MIN = -2147483648
_INT_MAX = 2147483647
_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


class OptionalTimeField(serializers.TimeField):
    """Time field that treats a blank value as null."""

    def to_internal_value(self, value):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        if isinstance(value, str):
            value = value.strip()
        return super().to_internal_value(value)


class OptionalCharField(serializers.CharField):
    """Text field that stores a blank value as null."""

    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('allow_null', True)
        kwargs.setdefault('allow_blank', True)
        kwargs.setdefault('trim_whitespace', True)
        kwargs.setdefault('default', None)
        super().__init__(**kwargs)

    def run_validation(self, data=serializers.empty):
        if data == '' or (
            self.trim_whitespace and isinstance(data, str) and data.strip() == ''
        ):
            return None
        return super().run_validation(data)


class Formulario2ACreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43edan_formulario_2a.

    Foreign keys and the evaluator role are checked by Formulario2AService.
    c_usuari_login is taken from the authenticated user, not from the body.
    estado_registro_id is required because the catalog ids are not assumed.
    numero_hoja defaults to 1, matching the column default.
    """

    emergencia_id = serializers.IntegerField(
        min_value=_INT_MIN,
        max_value=_INT_MAX,
        error_messages={
            'required': 'El campo emergencia_id es obligatorio',
            'null': 'El campo emergencia_id es obligatorio',
            'invalid': 'El campo emergencia_id debe ser un número entero',
            'min_value': 'El campo emergencia_id debe ser un número entero',
            'max_value': 'El campo emergencia_id debe ser un número entero',
        },
    )
    departamento_id = serializers.CharField(
        min_length=2,
        max_length=2,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo departamento_id es obligatorio',
            'blank': 'El campo departamento_id es obligatorio',
            'null': 'El campo departamento_id es obligatorio',
            'invalid': 'El campo departamento_id debe ser texto',
            'min_length': 'El campo departamento_id debe tener 2 caracteres',
            'max_length': 'El campo departamento_id debe tener 2 caracteres',
        },
    )
    provincia_id = serializers.CharField(
        min_length=2,
        max_length=2,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo provincia_id es obligatorio',
            'blank': 'El campo provincia_id es obligatorio',
            'null': 'El campo provincia_id es obligatorio',
            'invalid': 'El campo provincia_id debe ser texto',
            'min_length': 'El campo provincia_id debe tener 2 caracteres',
            'max_length': 'El campo provincia_id debe tener 2 caracteres',
        },
    )
    distrito_id = serializers.CharField(
        min_length=2,
        max_length=2,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo distrito_id es obligatorio',
            'blank': 'El campo distrito_id es obligatorio',
            'null': 'El campo distrito_id es obligatorio',
            'invalid': 'El campo distrito_id debe ser texto',
            'min_length': 'El campo distrito_id debe tener 2 caracteres',
            'max_length': 'El campo distrito_id debe tener 2 caracteres',
        },
    )
    fecha_empadronamiento = serializers.DateField(
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'El campo fecha_empadronamiento es obligatorio',
            'null': 'El campo fecha_empadronamiento es obligatorio',
            'invalid': 'El campo fecha_empadronamiento debe tener el formato AAAA-MM-DD',
        },
    )
    hora_empadronamiento = OptionalTimeField(
        required=False,
        allow_null=True,
        default=None,
        input_formats=['%H:%M:%S', '%H:%M'],
        error_messages={
            'invalid': (
                'El campo hora_empadronamiento debe tener el formato '
                'HH:MM o HH:MM:SS'
            ),
        },
    )
    localidad = OptionalCharField(
        max_length=200,
        error_messages={
            'invalid': 'El campo localidad debe ser texto',
            'max_length': 'El campo localidad no debe superar 200 caracteres',
        },
    )
    barrio_sector_urbanizacion = OptionalCharField(
        max_length=250,
        error_messages={
            'invalid': 'El campo barrio_sector_urbanizacion debe ser texto',
            'max_length': (
                'El campo barrio_sector_urbanizacion no debe superar 250 caracteres'
            ),
        },
    )
    centro_poblado = OptionalCharField(
        max_length=200,
        error_messages={
            'invalid': 'El campo centro_poblado debe ser texto',
            'max_length': 'El campo centro_poblado no debe superar 200 caracteres',
        },
    )
    caserio = OptionalCharField(
        max_length=200,
        error_messages={
            'invalid': 'El campo caserio debe ser texto',
            'max_length': 'El campo caserio no debe superar 200 caracteres',
        },
    )
    anexo = OptionalCharField(
        max_length=200,
        error_messages={
            'invalid': 'El campo anexo debe ser texto',
            'max_length': 'El campo anexo no debe superar 200 caracteres',
        },
    )
    calle_manzana = OptionalCharField(
        max_length=250,
        error_messages={
            'invalid': 'El campo calle_manzana debe ser texto',
            'max_length': 'El campo calle_manzana no debe superar 250 caracteres',
        },
    )
    edificio_piso_dpto = OptionalCharField(
        max_length=250,
        error_messages={
            'invalid': 'El campo edificio_piso_dpto debe ser texto',
            'max_length': 'El campo edificio_piso_dpto no debe superar 250 caracteres',
        },
    )
    otros_ubicacion = OptionalCharField(
        max_length=250,
        error_messages={
            'invalid': 'El campo otros_ubicacion debe ser texto',
            'max_length': 'El campo otros_ubicacion no debe superar 250 caracteres',
        },
    )
    numero_hoja = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=1,
        min_value=1,
        max_value=_SMALLINT_MAX,
        error_messages={
            'invalid': 'El campo numero_hoja debe ser un número entero mayor que cero',
            'min_value': 'El campo numero_hoja debe ser un número entero mayor que cero',
            'max_value': 'El campo numero_hoja debe ser un número entero mayor que cero',
        },
    )
    total_hojas = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        min_value=1,
        max_value=_SMALLINT_MAX,
        error_messages={
            'invalid': 'El campo total_hojas debe ser un número entero mayor que cero',
            'min_value': 'El campo total_hojas debe ser un número entero mayor que cero',
            'max_value': 'El campo total_hojas debe ser un número entero mayor que cero',
        },
    )
    institucion = OptionalCharField(
        max_length=250,
        error_messages={
            'invalid': 'El campo institucion debe ser texto',
            'max_length': 'El campo institucion no debe superar 250 caracteres',
        },
    )
    evaluador_id = serializers.IntegerField(
        min_value=_SMALLINT_MIN,
        max_value=_SMALLINT_MAX,
        error_messages={
            'required': 'El campo evaluador_id es obligatorio',
            'null': 'El campo evaluador_id es obligatorio',
            'invalid': 'El campo evaluador_id debe ser un número entero',
            'min_value': 'El campo evaluador_id debe ser un número entero',
            'max_value': 'El campo evaluador_id debe ser un número entero',
        },
    )
    estado_registro_id = serializers.IntegerField(
        min_value=_SMALLINT_MIN,
        max_value=_SMALLINT_MAX,
        error_messages={
            'required': 'El campo estado_registro_id es obligatorio',
            'null': 'El campo estado_registro_id es obligatorio',
            'invalid': 'El campo estado_registro_id debe ser un número entero',
            'min_value': 'El campo estado_registro_id debe ser un número entero',
            'max_value': 'El campo estado_registro_id debe ser un número entero',
        },
    )

    def validate_numero_hoja(self, value):
        if value is None:
            return 1
        return value

    def validate(self, attrs):
        total_hojas = attrs.get('total_hojas')
        numero_hoja = attrs.get('numero_hoja', 1)
        if total_hojas is not None and total_hojas < numero_hoja:
            raise serializers.ValidationError(
                {
                    'total_hojas': (
                        'El campo total_hojas debe ser mayor o igual que numero_hoja'
                    ),
                }
            )
        return attrs


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
