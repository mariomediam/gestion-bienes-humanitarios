from rest_framework import serializers

from .movimiento import (
    MovimientoCreateSerializer,
    MovimientoSerializer,
    _OptionalCharField,
    _OptionalDateTimeField,
    _int_field,
)

_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767
_INT_MIN = -2147483648
_INT_MAX = 2147483647


class PlanillaEntregaTotalSerializer(serializers.Serializer):
    """Count of rows in S43bah_planilla_entrega."""

    total = serializers.IntegerField(min_value=0)


class Formulario2ATienePlanillaBahSerializer(serializers.Serializer):
    """Whether one Formulario 2A already has a BAH planilla."""

    tiene_planilla_bah = serializers.BooleanField()


class PlanillaEntregaCreateSerializer(MovimientoCreateSerializer):
    """Validate the body used to insert a planilla BAH and its movement.

    Movement fields match the warehouse create. observacion belongs to the
    movement. planilla_entrega_observacion is S43bah_planilla_entrega.observacion.
    fecha_anulacion, motivo_anulacion, c_usuari_login, fecha_creacion,
    fecha_modificacion and movimiento_almacen_id are not accepted.
    numero_planilla may be omitted; the service then assigns the next number
    of anio_planilla. Existence of the receptor, the planilla state and the
    one-planilla-per-formulario rule are checked by PlanillaEntregaService.
    """

    anio_planilla = _int_field('anio_planilla', minimum=_INT_MIN, maximum=_INT_MAX)
    numero_planilla = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        min_value=_INT_MIN,
        max_value=_INT_MAX,
        error_messages={
            'invalid': 'El campo numero_planilla debe ser un número entero',
            'min_value': 'El campo numero_planilla debe ser un número entero',
            'max_value': 'El campo numero_planilla debe ser un número entero',
        },
    )
    integrante_receptor_id = _int_field(
        'integrante_receptor_id',
        minimum=_INT_MIN,
        maximum=_INT_MAX,
    )
    fecha_entrega = serializers.DateField(
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'El campo fecha_entrega es obligatorio',
            'null': 'El campo fecha_entrega es obligatorio',
            'invalid': 'El campo fecha_entrega debe tener el formato AAAA-MM-DD',
        },
    )
    estado_planilla_id = _int_field(
        'estado_planilla_id',
        minimum=_SMALLINT_MIN,
        maximum=_SMALLINT_MAX,
    )
    planilla_entrega_observacion = _OptionalCharField(
        max_length=1000,
        error_messages={
            'invalid': 'El campo planilla_entrega_observacion debe ser texto',
            'max_length': (
                'El campo planilla_entrega_observacion no debe superar '
                '1000 caracteres'
            ),
        },
    )
    fecha_emision = _OptionalDateTimeField(
        error_messages={
            'invalid': (
                'El campo fecha_emision debe tener el formato '
                'AAAA-MM-DD HH:MM:SS'
            ),
        },
    )


class PlanillaEntregaSerializer(serializers.Serializer):
    """Stored planilla BAH with the warehouse movement created with it."""

    planilla_entrega_id = serializers.IntegerField()
    numero_planilla = serializers.IntegerField()
    anio_planilla = serializers.IntegerField()
    integrante_receptor_id = serializers.IntegerField()
    fecha_entrega = serializers.DateField()
    estado_planilla_id = serializers.IntegerField()
    observacion = serializers.CharField(allow_null=True)
    fecha_emision = serializers.DateTimeField(allow_null=True)
    fecha_anulacion = serializers.DateTimeField(allow_null=True)
    motivo_anulacion = serializers.CharField(allow_null=True)
    c_usuari_login = serializers.CharField()
    fecha_creacion = serializers.DateTimeField()
    fecha_modificacion = serializers.DateTimeField(allow_null=True)
    movimiento_almacen_id = serializers.IntegerField()
    movimiento = MovimientoSerializer(source='movimiento_almacen')
