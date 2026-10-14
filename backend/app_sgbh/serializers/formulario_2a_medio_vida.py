from rest_framework import serializers

_INT_MIN = -2147483648
_INT_MAX = 2147483647
_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767
_OBSERVACION_MAX_LENGTH = 500


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


def _id_field(name, *, smallint=True):
    """Required integer foreign key with the Spanish messages used by the API."""
    obligatorio = f'El campo {name} es obligatorio'
    invalido = f'El campo {name} debe ser un número entero'
    return serializers.IntegerField(
        min_value=_SMALLINT_MIN if smallint else _INT_MIN,
        max_value=_SMALLINT_MAX if smallint else _INT_MAX,
        error_messages={
            'required': obligatorio,
            'null': obligatorio,
            'invalid': invalido,
            'min_value': invalido,
            'max_value': invalido,
        },
    )


class MedioVidaCreateSerializer(serializers.Serializer):
    """Validate the body used to insert S43edan_formulario_2a_medios_vida.

    Foreign keys, the unique pair familia and tipo, and the parent form
    lock are checked by Formulario2AMedioVidaService. fecha_creacion uses
    the column default. cantidad follows the table check (greater than zero).
    """

    familia_id = _id_field('familia_id', smallint=False)
    tipo_medio_vida_id = _id_field('tipo_medio_vida_id')
    cantidad = serializers.IntegerField(
        min_value=1,
        max_value=_INT_MAX,
        error_messages={
            'required': 'El campo cantidad es obligatorio',
            'null': 'El campo cantidad es obligatorio',
            'invalid': 'El campo cantidad debe ser un número entero',
            'min_value': 'El campo cantidad debe ser mayor que cero',
            'max_value': 'El campo cantidad debe ser un número entero',
        },
    )
    observacion = OptionalCharField(
        max_length=_OBSERVACION_MAX_LENGTH,
        error_messages={
            'invalid': 'El campo observacion debe ser texto',
            'max_length': (
                'El campo observacion no debe superar 500 caracteres'
            ),
        },
    )


class MedioVidaSerializer(serializers.Serializer):
    """One medio de vida row returned after it is created.

    Catalog names follow the related tipo and its categoria.
    """

    medio_vida_id = serializers.IntegerField()
    familia_id = serializers.IntegerField()
    tipo_medio_vida_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    observacion = serializers.CharField(allow_null=True)
    fecha_creacion = serializers.DateTimeField()
    tipo_medio_vida_nombre = serializers.CharField(
        source='tipo_medio_vida.nombre',
    )
    categoria_medio_vida_id = serializers.IntegerField(
        source='tipo_medio_vida.categoria_medio_vida_id',
    )
    categoria_medio_vida_nombre = serializers.CharField(
        source='tipo_medio_vida.categoria_medio_vida.nombre',
    )
