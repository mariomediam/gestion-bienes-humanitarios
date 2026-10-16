from rest_framework import serializers

_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


class _ClearableCharField(serializers.CharField):
    """Optional text. A missing value stays missing. Blank is stored as null."""

    def __init__(self, **kwargs):
        kwargs['required'] = False
        kwargs['allow_null'] = True
        kwargs['allow_blank'] = True
        kwargs.setdefault('trim_whitespace', True)
        super().__init__(**kwargs)

    def validate_empty_values(self, data):
        if data is serializers.empty:
            return super().validate_empty_values(data)
        if data is None or data == '' or (
            self.trim_whitespace and isinstance(data, str) and data.strip() == ''
        ):
            return (True, None)
        return super().validate_empty_values(data)


class _ClearableOrdenField(serializers.IntegerField):
    """Optional smallint. A missing value stays missing. Blank is stored as null."""

    def __init__(self, **kwargs):
        kwargs['required'] = False
        kwargs['allow_null'] = True
        kwargs['min_value'] = 1
        kwargs['max_value'] = _SMALLINT_MAX
        super().__init__(**kwargs)

    def validate_empty_values(self, data):
        if data is serializers.empty:
            return super().validate_empty_values(data)
        if data is None or data == '' or (
            isinstance(data, str) and data.strip() == ''
        ):
            return (True, None)
        return super().validate_empty_values(data)


class BienCreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43cat_bah_bienes.

    descripcion is not accepted and is stored as null. orden_impresion is
    not accepted: BienService sets it to the current maximum plus one.
    Category and unit existence, and codigo uniqueness, are checked there.
    An inactive category or unit is accepted.
    """

    categoria_bien_id = serializers.IntegerField(
        min_value=_SMALLINT_MIN,
        max_value=_SMALLINT_MAX,
        error_messages={
            'required': 'El campo categoria_bien_id es obligatorio',
            'invalid': 'El campo categoria_bien_id debe ser un número entero',
            'null': 'El campo categoria_bien_id es obligatorio',
            'min_value': 'El campo categoria_bien_id debe ser un número entero',
            'max_value': 'El campo categoria_bien_id debe ser un número entero',
        },
    )
    unidad_medida_id = serializers.IntegerField(
        min_value=_SMALLINT_MIN,
        max_value=_SMALLINT_MAX,
        error_messages={
            'required': 'El campo unidad_medida_id es obligatorio',
            'invalid': 'El campo unidad_medida_id debe ser un número entero',
            'null': 'El campo unidad_medida_id es obligatorio',
            'min_value': 'El campo unidad_medida_id debe ser un número entero',
            'max_value': 'El campo unidad_medida_id debe ser un número entero',
        },
    )
    codigo = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo codigo es obligatorio',
            'blank': 'El campo codigo es obligatorio',
            'null': 'El campo codigo es obligatorio',
            'invalid': 'El campo codigo debe ser texto',
            'max_length': 'El campo codigo no debe superar 50 caracteres',
        },
    )
    nombre = serializers.CharField(
        max_length=250,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo nombre es obligatorio',
            'blank': 'El campo nombre es obligatorio',
            'null': 'El campo nombre es obligatorio',
            'invalid': 'El campo nombre debe ser texto',
            'max_length': 'El campo nombre no debe superar 250 caracteres',
        },
    )
    esta_activo = serializers.BooleanField(
        error_messages={
            'required': 'El campo esta_activo es obligatorio',
            'invalid': 'El campo esta_activo debe ser 1, 0, true o false',
            'null': 'El campo esta_activo es obligatorio',
        },
    )
    visible_planilla = serializers.BooleanField(
        error_messages={
            'required': 'El campo visible_planilla es obligatorio',
            'invalid': 'El campo visible_planilla debe ser 1, 0, true o false',
            'null': 'El campo visible_planilla es obligatorio',
        },
    )


class BienUpdateSerializer(serializers.Serializer):
    """Validate a partial update of S43cat_bah_bienes.

    Only keys present in the body are returned. codigo cannot be changed.
    categoria_bien_id and unidad_medida_id are checked by BienService.
    An inactive category or unit is accepted.
    """

    categoria_bien_id = serializers.IntegerField(
        required=False,
        min_value=_SMALLINT_MIN,
        max_value=_SMALLINT_MAX,
        error_messages={
            'invalid': 'El campo categoria_bien_id debe ser un número entero',
            'null': 'El campo categoria_bien_id es obligatorio',
            'min_value': 'El campo categoria_bien_id debe ser un número entero',
            'max_value': 'El campo categoria_bien_id debe ser un número entero',
        },
    )
    unidad_medida_id = serializers.IntegerField(
        required=False,
        min_value=_SMALLINT_MIN,
        max_value=_SMALLINT_MAX,
        error_messages={
            'invalid': 'El campo unidad_medida_id debe ser un número entero',
            'null': 'El campo unidad_medida_id es obligatorio',
            'min_value': 'El campo unidad_medida_id debe ser un número entero',
            'max_value': 'El campo unidad_medida_id debe ser un número entero',
        },
    )
    nombre = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=250,
        trim_whitespace=True,
        error_messages={
            'blank': 'El campo nombre es obligatorio',
            'null': 'El campo nombre es obligatorio',
            'invalid': 'El campo nombre debe ser texto',
            'max_length': 'El campo nombre no debe superar 250 caracteres',
        },
    )
    descripcion = _ClearableCharField(
        max_length=500,
        error_messages={
            'invalid': 'El campo descripcion debe ser texto',
            'max_length': 'El campo descripcion no debe superar 500 caracteres',
        },
    )
    orden_impresion = _ClearableOrdenField(
        error_messages={
            'invalid': 'El campo orden_impresion debe ser un número entero',
            'min_value': 'El campo orden_impresion debe ser mayor que 0',
            'max_value': 'El campo orden_impresion debe ser un número entero',
        },
    )
    esta_activo = serializers.BooleanField(
        required=False,
        error_messages={
            'invalid': 'El campo esta_activo debe ser 1, 0, true o false',
            'null': 'El campo esta_activo es obligatorio',
        },
    )
    visible_planilla = serializers.BooleanField(
        required=False,
        error_messages={
            'invalid': 'El campo visible_planilla debe ser 1, 0, true o false',
            'null': 'El campo visible_planilla es obligatorio',
        },
    )

    def validate(self, attrs):
        if isinstance(self.initial_data, dict) and 'codigo' in self.initial_data:
            raise serializers.ValidationError(
                'El campo codigo no se puede modificar'
            )
        return attrs


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
