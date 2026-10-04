from rest_framework import serializers

from .formulario_2a import Formulario2AUbicacionSerializer

_INT_MIN = -2147483648
_INT_MAX = 2147483647


class OptionalTimeField(serializers.TimeField):
    """Time field that treats a blank value as null."""

    def to_internal_value(self, value):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        if isinstance(value, str):
            value = value.strip()
        return super().to_internal_value(value)


class EmergenciaCreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43edan_emergencias.

    Uniqueness of codigo_sinpad and the tipo_peligro foreign key are
    checked by EmergenciaService, which performs the insert.
    c_usuari_login is taken from the authenticated user, not from the body.
    """

    numero_evaluacion = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo numero_evaluacion es obligatorio',
            'blank': 'El campo numero_evaluacion es obligatorio',
            'null': 'El campo numero_evaluacion es obligatorio',
            'invalid': 'El campo numero_evaluacion debe ser texto',
            'max_length': 'El campo numero_evaluacion no debe superar 50 caracteres',
        },
    )
    codigo_sinpad = serializers.CharField(
        max_length=30,
        trim_whitespace=True,
        error_messages={
            'required': 'El campo codigo_sinpad es obligatorio',
            'blank': 'El campo codigo_sinpad es obligatorio',
            'null': 'El campo codigo_sinpad es obligatorio',
            'invalid': 'El campo codigo_sinpad debe ser texto',
            'max_length': 'El campo codigo_sinpad no debe superar 30 caracteres',
        },
    )
    tipo_peligro_id = serializers.IntegerField(
        min_value=_INT_MIN,
        max_value=_INT_MAX,
        error_messages={
            'required': 'El campo tipo_peligro_id es obligatorio',
            'null': 'El campo tipo_peligro_id es obligatorio',
            'invalid': 'El campo tipo_peligro_id debe ser un número entero',
            'min_value': 'El campo tipo_peligro_id debe ser un número entero',
            'max_value': 'El campo tipo_peligro_id debe ser un número entero',
        },
    )
    fecha_emergencia = serializers.DateField(
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'El campo fecha_emergencia es obligatorio',
            'null': 'El campo fecha_emergencia es obligatorio',
            'invalid': 'El campo fecha_emergencia debe tener el formato AAAA-MM-DD',
        },
    )
    hora_ocurrencia_estimada = OptionalTimeField(
        required=False,
        allow_null=True,
        default=None,
        input_formats=['%H:%M:%S', '%H:%M'],
        error_messages={
            'invalid': (
                'El campo hora_ocurrencia_estimada debe tener el formato '
                'HH:MM o HH:MM:SS'
            ),
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


class EmergenciaSerializer(serializers.Serializer):
    """Emergency payload returned by the list, search and create endpoints."""

    emergencia_id = serializers.IntegerField()
    numero_evaluacion = serializers.CharField()
    codigo_sinpad = serializers.CharField(allow_null=True)
    tipo_peligro_id = serializers.IntegerField()
    fecha_emergencia = serializers.DateField()
    hora_ocurrencia_estimada = serializers.TimeField(allow_null=True)
    esta_activo = serializers.BooleanField()
    c_usuari_login = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_modificacion = serializers.DateTimeField(allow_null=True)
    nombre_tipo_peligro = serializers.CharField(source='tipo_peligro.nombre')
    formularios_2a = Formulario2AUbicacionSerializer(many=True)


def first_error_message(errors):
    """Return the first serializer error as a single Spanish message."""
    for messages in errors.values():
        if isinstance(messages, (list, tuple)) and messages:
            return str(messages[0])
        if isinstance(messages, str):
            return messages
    return 'Los datos enviados no son válidos'
