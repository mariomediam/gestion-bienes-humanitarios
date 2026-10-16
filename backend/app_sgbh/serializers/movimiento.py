from rest_framework import serializers

_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767
_INT_MIN = -2147483648
_INT_MAX = 2147483647


def _int_field(name, *, minimum, maximum):
    return serializers.IntegerField(
        min_value=minimum,
        max_value=maximum,
        error_messages={
            'required': f'El campo {name} es obligatorio',
            'invalid': f'El campo {name} debe ser un número entero',
            'null': f'El campo {name} es obligatorio',
            'min_value': f'El campo {name} debe ser un número entero',
            'max_value': f'El campo {name} debe ser un número entero',
        },
    )


class _OptionalCharField(serializers.CharField):
    """Optional text. A missing or blank value is stored as null."""

    def __init__(self, **kwargs):
        kwargs['required'] = False
        kwargs['allow_null'] = True
        kwargs['allow_blank'] = True
        kwargs['default'] = None
        kwargs.setdefault('trim_whitespace', True)
        super().__init__(**kwargs)

    def validate_empty_values(self, data):
        if data is None or data == '' or (
            isinstance(data, str) and data.strip() == ''
        ):
            return (True, None)
        return super().validate_empty_values(data)


class _OptionalDateTimeField(serializers.DateTimeField):
    """Optional datetime. A missing or blank value is stored as null."""

    def __init__(self, **kwargs):
        kwargs['required'] = False
        kwargs['allow_null'] = True
        kwargs['default'] = None
        kwargs.setdefault('input_formats', ['iso-8601'])
        super().__init__(**kwargs)

    def to_internal_value(self, value):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        if isinstance(value, str):
            value = value.strip()
        return super().to_internal_value(value)


class _OptionalDateField(serializers.DateField):
    """Optional date. A missing or blank value is stored as null."""

    def __init__(self, **kwargs):
        kwargs['required'] = False
        kwargs['allow_null'] = True
        kwargs['default'] = None
        kwargs.setdefault('input_formats', ['%Y-%m-%d'])
        super().__init__(**kwargs)

    def to_internal_value(self, value):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        if isinstance(value, str):
            value = value.strip()
        return super().to_internal_value(value)


class MovimientoDetalleCreateSerializer(serializers.Serializer):
    """Validate one S43alm_movimiento_detalle row sent on create."""

    bien_id = _int_field('bien_id', minimum=_INT_MIN, maximum=_INT_MAX)
    cantidad = serializers.DecimalField(
        max_digits=18,
        decimal_places=6,
        error_messages={
            'required': 'El campo cantidad es obligatorio',
            'null': 'El campo cantidad es obligatorio',
            'invalid': 'El campo cantidad debe ser un número decimal',
            'max_digits': (
                'El campo cantidad debe tener como máximo 18 dígitos y 6 decimales'
            ),
            'max_decimal_places': (
                'El campo cantidad debe tener como máximo 18 dígitos y 6 decimales'
            ),
            'max_whole_digits': (
                'El campo cantidad debe tener como máximo 18 dígitos y 6 decimales'
            ),
        },
    )
    cantidad_texto = _OptionalCharField(
        max_length=30,
        error_messages={
            'invalid': 'El campo cantidad_texto debe ser texto',
            'max_length': 'El campo cantidad_texto no debe superar 30 caracteres',
        },
    )
    es_devolvible = serializers.BooleanField(
        error_messages={
            'required': 'El campo es_devolvible es obligatorio',
            'invalid': 'El campo es_devolvible debe ser 1, 0, true o false',
            'null': 'El campo es_devolvible es obligatorio',
        },
    )
    observacion = _OptionalCharField(
        max_length=500,
        error_messages={
            'invalid': 'El campo observacion debe ser texto',
            'max_length': 'El campo observacion no debe superar 500 caracteres',
        },
    )

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError('Cada detalle debe ser un objeto')
        return super().to_internal_value(data)


class MovimientoCreateSerializer(serializers.Serializer):
    """Validate the body used to insert a warehouse movement and its details.

    fecha_creacion and fecha_modificacion are not accepted. Existence,
    active flags, quantity sign and movimiento_origen_id are checked by
    MovimientoService.
    """

    almacen_id = _int_field('almacen_id', minimum=_INT_MIN, maximum=_INT_MAX)
    tipo_movimiento_id = _int_field(
        'tipo_movimiento_id',
        minimum=_SMALLINT_MIN,
        maximum=_SMALLINT_MAX,
    )
    estado_movimiento_id = _int_field(
        'estado_movimiento_id',
        minimum=_SMALLINT_MIN,
        maximum=_SMALLINT_MAX,
    )
    movimiento_origen_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        min_value=_INT_MIN,
        max_value=_INT_MAX,
        error_messages={
            'invalid': 'El campo movimiento_origen_id debe ser un número entero',
            'min_value': 'El campo movimiento_origen_id debe ser un número entero',
            'max_value': 'El campo movimiento_origen_id debe ser un número entero',
        },
    )
    fecha_movimiento = serializers.DateTimeField(
        input_formats=['iso-8601'],
        error_messages={
            'required': 'El campo fecha_movimiento es obligatorio',
            'null': 'El campo fecha_movimiento es obligatorio',
            'invalid': (
                'El campo fecha_movimiento debe tener el formato '
                'AAAA-MM-DD HH:MM:SS'
            ),
        },
    )
    documento_referencia = _OptionalCharField(
        max_length=100,
        error_messages={
            'invalid': 'El campo documento_referencia debe ser texto',
            'max_length': (
                'El campo documento_referencia no debe superar 100 caracteres'
            ),
        },
    )
    fecha_documento = _OptionalDateField(
        error_messages={
            'invalid': 'El campo fecha_documento debe tener el formato AAAA-MM-DD',
        },
    )
    destinatario = _OptionalCharField(
        max_length=250,
        error_messages={
            'invalid': 'El campo destinatario debe ser texto',
            'max_length': 'El campo destinatario no debe superar 250 caracteres',
        },
    )
    observacion = _OptionalCharField(
        max_length=1000,
        error_messages={
            'invalid': 'El campo observacion debe ser texto',
            'max_length': 'El campo observacion no debe superar 1000 caracteres',
        },
    )
    fecha_confirmacion = _OptionalDateTimeField(
        error_messages={
            'invalid': (
                'El campo fecha_confirmacion debe tener el formato '
                'AAAA-MM-DD HH:MM:SS'
            ),
        },
    )
    encargado_almacen_id = _int_field(
        'encargado_almacen_id',
        minimum=_SMALLINT_MIN,
        maximum=_SMALLINT_MAX,
    )
    c_usuari_login = serializers.CharField(
        max_length=20,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo c_usuari_login es obligatorio',
            'blank': 'El campo c_usuari_login es obligatorio',
            'null': 'El campo c_usuari_login es obligatorio',
            'invalid': 'El campo c_usuari_login debe ser texto',
            'max_length': 'El campo c_usuari_login no debe superar 20 caracteres',
        },
    )
    detalles = serializers.ListField(
        child=MovimientoDetalleCreateSerializer(),
        allow_empty=False,
        error_messages={
            'required': 'El campo detalles es obligatorio',
            'null': 'El campo detalles es obligatorio',
            'not_a_list': 'El campo detalles debe ser una lista',
            'empty': 'Debe registrar al menos un detalle',
        },
    )


class MovimientoDetalleSerializer(serializers.Serializer):
    """One stored S43alm_movimiento_detalle row."""

    movimiento_detalle_id = serializers.IntegerField()
    movimiento_id = serializers.IntegerField()
    bien_id = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=18, decimal_places=6)
    cantidad_texto = serializers.CharField(allow_null=True)
    es_devolvible = serializers.BooleanField()
    observacion = serializers.CharField(allow_null=True)
    fecha_creacion = serializers.DateTimeField()


class MovimientoSerializer(serializers.Serializer):
    """Stored S43alm_movimientos row with its details."""

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
    detalles = MovimientoDetalleSerializer(many=True)
