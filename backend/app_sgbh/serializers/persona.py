from rest_framework import serializers

_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


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


class OptionalSmallIntField(serializers.IntegerField):
    """Smallint field that treats a blank value as null."""

    def run_validation(self, data=serializers.empty):
        if data is None or data == '' or (
            isinstance(data, str) and data.strip() == ''
        ):
            if not self.allow_null:
                self.fail('null')
            return None
        return super().run_validation(data)


class PersonaCreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43personas.

    The tipo_documento foreign key is checked by PersonaService.
    tipo_documento_id and numero_documento must both be present or both empty,
    matching CK_personas_documento.
    c_usuari_login is taken from the authenticated user, not from the body.
    esta_activo defaults to true, matching the column default.
    """

    tipo_documento_id = OptionalSmallIntField(
        required=False,
        allow_null=True,
        default=None,
        min_value=_SMALLINT_MIN,
        max_value=_SMALLINT_MAX,
        error_messages={
            'invalid': 'El campo tipo_documento_id debe ser un número entero',
            'min_value': 'El campo tipo_documento_id debe ser un número entero',
            'max_value': 'El campo tipo_documento_id debe ser un número entero',
        },
    )
    numero_documento = OptionalCharField(
        max_length=20,
        error_messages={
            'invalid': 'El campo numero_documento debe ser texto',
            'max_length': 'El campo numero_documento no debe superar 20 caracteres',
        },
    )
    apellido_paterno = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo apellido_paterno es obligatorio',
            'blank': 'El campo apellido_paterno es obligatorio',
            'null': 'El campo apellido_paterno es obligatorio',
            'invalid': 'El campo apellido_paterno debe ser texto',
            'max_length': 'El campo apellido_paterno no debe superar 50 caracteres',
        },
    )
    apellido_materno = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo apellido_materno es obligatorio',
            'blank': 'El campo apellido_materno es obligatorio',
            'null': 'El campo apellido_materno es obligatorio',
            'invalid': 'El campo apellido_materno debe ser texto',
            'max_length': 'El campo apellido_materno no debe superar 50 caracteres',
        },
    )
    nombres = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo nombres es obligatorio',
            'blank': 'El campo nombres es obligatorio',
            'null': 'El campo nombres es obligatorio',
            'invalid': 'El campo nombres debe ser texto',
            'max_length': 'El campo nombres no debe superar 150 caracteres',
        },
    )
    fecha_nacimiento = serializers.DateField(
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'El campo fecha_nacimiento es obligatorio',
            'null': 'El campo fecha_nacimiento es obligatorio',
            'invalid': 'El campo fecha_nacimiento debe tener el formato AAAA-MM-DD',
        },
    )
    sexo = serializers.CharField(
        min_length=1,
        max_length=1,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo sexo es obligatorio',
            'blank': 'El campo sexo es obligatorio',
            'null': 'El campo sexo es obligatorio',
            'invalid': 'El campo sexo debe ser texto',
            'min_length': 'El campo sexo debe tener 1 carácter',
            'max_length': 'El campo sexo debe tener 1 carácter',
        },
    )
    telefono = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo telefono es obligatorio',
            'blank': 'El campo telefono es obligatorio',
            'null': 'El campo telefono es obligatorio',
            'invalid': 'El campo telefono debe ser texto',
            'max_length': 'El campo telefono no debe superar 50 caracteres',
        },
    )
    correo = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo correo es obligatorio',
            'blank': 'El campo correo es obligatorio',
            'null': 'El campo correo es obligatorio',
            'invalid': 'El campo correo debe ser texto',
            'max_length': 'El campo correo no debe superar 50 caracteres',
        },
    )
    esta_activo = serializers.BooleanField(
        required=False,
        allow_null=True,
        default=True,
        error_messages={
            'invalid': 'El campo esta_activo debe ser 1, 0, true o false',
        },
    )

    def validate_esta_activo(self, value):
        if value is None:
            return True
        return value

    def validate(self, attrs):
        tipo_documento_id = attrs.get('tipo_documento_id')
        numero_documento = attrs.get('numero_documento')
        if (tipo_documento_id is None) != (numero_documento is None):
            raise serializers.ValidationError(
                'Los campos tipo_documento_id y numero_documento deben enviarse juntos o ambos vacíos'
            )
        return attrs


class PersonaSerializer(serializers.Serializer):
    """Person payload returned by the create endpoint."""

    persona_id = serializers.IntegerField()
    tipo_documento_id = serializers.IntegerField(allow_null=True)
    numero_documento = serializers.CharField(allow_null=True)
    apellido_paterno = serializers.CharField()
    apellido_materno = serializers.CharField()
    nombres = serializers.CharField()
    fecha_nacimiento = serializers.DateField()
    sexo = serializers.CharField()
    telefono = serializers.CharField()
    correo = serializers.CharField()
    esta_activo = serializers.BooleanField()
    c_usuari_login = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_modificacion = serializers.DateTimeField(allow_null=True)
    nombre_tipo_documento = serializers.SerializerMethodField()

    def get_nombre_tipo_documento(self, obj):
        tipo_documento = getattr(obj, 'tipo_documento', None)
        if tipo_documento is None:
            return None
        return tipo_documento.nombre
