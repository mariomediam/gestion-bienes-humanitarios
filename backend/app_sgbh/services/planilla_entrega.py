from datetime import date, datetime

from django.db import IntegrityError, transaction
from django.db.models import Count, Max
from django.utils import timezone

from ..db_router import DB_ALIAS
from ..models import EstadoPlanilla, Formulario2AIntegrante, PlanillaEntrega
from .movimiento import MovimientoService

_INT_MIN = -2147483648
_INT_MAX = 2147483647
_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


class PlanillaEntregaServiceError(Exception):
    """Business rule violation for a BAH planilla operation."""

    def __init__(self, message, *, not_found=False, conflict=False):
        super().__init__(message)
        self.message = message
        self.not_found = not_found
        self.conflict = conflict


class PlanillaEntregaService:
    @staticmethod
    def count(estado_planilla_id=None):
        """Count rows in S43bah_planilla_entrega.

        Optional filter on estado_planilla_id. When omitted, every row is counted.
        """
        queryset = PlanillaEntrega.objects.all()
        if estado_planilla_id is not None:
            queryset = queryset.filter(estado_planilla_id=estado_planilla_id)
        result = queryset.aggregate(total=Count('*'))
        return result['total']

    @staticmethod
    def create(
        *,
        almacen_id,
        tipo_movimiento_id,
        estado_movimiento_id,
        movimiento_origen_id,
        fecha_movimiento,
        documento_referencia,
        fecha_documento,
        destinatario,
        observacion,
        fecha_confirmacion,
        encargado_almacen_id,
        c_usuari_login,
        detalles,
        anio_planilla,
        numero_planilla,
        integrante_receptor_id,
        fecha_entrega,
        estado_planilla_id,
        planilla_entrega_observacion,
        fecha_emision,
    ):
        """Insert one planilla BAH and its warehouse movement.

        Header, movement and detail rows are written in one transaction.
        Movement rules are the same as MovimientoService.create. anio_planilla
        is required. numero_planilla is stored when sent; otherwise it is one
        more than the maximum numero_planilla of that year, or 1 when the
        year has none. fecha_anulacion and motivo_anulacion stay null.
        c_usuari_login comes from the authenticated user and is the login
        stored on the movement. A formulario 2A can have only one planilla.
        """
        planilla = _clean_planilla(
            anio_planilla=anio_planilla,
            numero_planilla=numero_planilla,
            integrante_receptor_id=integrante_receptor_id,
            fecha_entrega=fecha_entrega,
            estado_planilla_id=estado_planilla_id,
            planilla_entrega_observacion=planilla_entrega_observacion,
            fecha_emision=fecha_emision,
        )

        with transaction.atomic(using=DB_ALIAS):
            formulario_2a_id = formulario_2a_id_de_integrante(
                planilla['integrante_receptor_id']
            )
            if formulario_2a_id is None:
                raise PlanillaEntregaServiceError(
                    'El integrante receptor indicado no existe'
                )
            if formulario_tiene_planilla_bah(formulario_2a_id):
                raise PlanillaEntregaServiceError(
                    'El formulario EDAN 2A ya tiene registrada una planilla BAH',
                    conflict=True,
                )
            _require_estado_planilla(planilla['estado_planilla_id'])
            if planilla['numero_planilla'] is None:
                planilla['numero_planilla'] = _siguiente_numero_planilla(
                    planilla['anio_planilla']
                )

            movimiento = MovimientoService.create(
                almacen_id=almacen_id,
                tipo_movimiento_id=tipo_movimiento_id,
                estado_movimiento_id=estado_movimiento_id,
                movimiento_origen_id=movimiento_origen_id,
                fecha_movimiento=fecha_movimiento,
                documento_referencia=documento_referencia,
                fecha_documento=fecha_documento,
                destinatario=destinatario,
                observacion=observacion,
                fecha_confirmacion=fecha_confirmacion,
                encargado_almacen_id=encargado_almacen_id,
                c_usuari_login=c_usuari_login,
                detalles=detalles,
            )

            row = PlanillaEntrega(
                numero_planilla=planilla['numero_planilla'],
                anio_planilla=planilla['anio_planilla'],
                integrante_receptor_id=planilla['integrante_receptor_id'],
                fecha_entrega=planilla['fecha_entrega'],
                estado_planilla_id=planilla['estado_planilla_id'],
                observacion=planilla['planilla_entrega_observacion'],
                fecha_emision=planilla['fecha_emision'],
                fecha_anulacion=None,
                motivo_anulacion=None,
                c_usuari_login=movimiento.c_usuari_login,
                fecha_creacion=timezone.now(),
                fecha_modificacion=None,
                movimiento_almacen=movimiento,
            )
            try:
                row.save()
            except IntegrityError:
                raise PlanillaEntregaServiceError(
                    'No se pudo registrar la planilla BAH'
                ) from None
        return row


def formulario_2a_id_de_integrante(integrante_receptor_id):
    """Return the Formulario 2A id reached from an integrante.

    The chain is integrante, familia, vivienda and formulario. Returns None
    when the integrante does not exist. Create starts here because the
    planilla row does not exist yet.
    """
    return (
        Formulario2AIntegrante.objects.filter(pk=integrante_receptor_id)
        .values_list('familia__vivienda__formulario_2a_id', flat=True)
        .first()
    )


def formulario_tiene_planilla_bah(
    formulario_2a_id,
    *,
    excluir_planilla_entrega_id=None,
):
    """Return whether this Formulario 2A already has a BAH planilla.

    Any planilla counts, whatever its estado. The link is the receptor
    integrante, its familia, its vivienda and the formulario.
    excluir_planilla_entrega_id omits that row so a later update can keep
    the same formulario, or move the planilla to another formulario that
    has none, without counting the planilla being edited.
    """
    queryset = PlanillaEntrega.objects.filter(
        integrante_receptor__familia__vivienda__formulario_2a_id=formulario_2a_id,
    )
    if excluir_planilla_entrega_id is not None:
        queryset = queryset.exclude(pk=excluir_planilla_entrega_id)
    return queryset.exists()


def _siguiente_numero_planilla(anio_planilla):
    """Next numero_planilla for one year. 1 when that year has no rows."""
    maximo = PlanillaEntrega.objects.filter(
        anio_planilla=anio_planilla,
    ).aggregate(maximo=Max('numero_planilla'))['maximo']
    if maximo is None:
        return 1
    if maximo >= _INT_MAX:
        raise PlanillaEntregaServiceError(
            'No se pudo asignar el número de planilla'
        )
    return maximo + 1


def _require_estado_planilla(estado_planilla_id):
    row = EstadoPlanilla.objects.filter(pk=estado_planilla_id).first()
    if row is None:
        raise PlanillaEntregaServiceError(
            'El estado de planilla indicado no existe'
        )
    if not row.esta_activo:
        raise PlanillaEntregaServiceError(
            'El estado de planilla indicado no está activo'
        )


def _clean_planilla(
    *,
    anio_planilla,
    numero_planilla,
    integrante_receptor_id,
    fecha_entrega,
    estado_planilla_id,
    planilla_entrega_observacion,
    fecha_emision,
):
    return {
        'anio_planilla': _require_int_id(anio_planilla, 'anio_planilla'),
        'numero_planilla': _optional_int_id(numero_planilla, 'numero_planilla'),
        'integrante_receptor_id': _require_int_id(
            integrante_receptor_id,
            'integrante_receptor_id',
        ),
        'fecha_entrega': _require_date(fecha_entrega, 'fecha_entrega'),
        'estado_planilla_id': _require_smallint_id(
            estado_planilla_id,
            'estado_planilla_id',
        ),
        'planilla_entrega_observacion': _optional_text(
            planilla_entrega_observacion,
            'planilla_entrega_observacion',
            1000,
        ),
        'fecha_emision': _optional_datetime(fecha_emision, 'fecha_emision'),
    }


def _require_int_id(value, field_name):
    if value is None:
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} es obligatorio'
        )
    return _check_int(value, field_name, _INT_MIN, _INT_MAX)


def _require_smallint_id(value, field_name):
    if value is None:
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} es obligatorio'
        )
    return _check_int(value, field_name, _SMALLINT_MIN, _SMALLINT_MAX)


def _optional_int_id(value, field_name):
    if value is None:
        return None
    return _check_int(value, field_name, _INT_MIN, _INT_MAX)


def _check_int(value, field_name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int):
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} debe ser un número entero'
        )
    if value < minimum or value > maximum:
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} debe ser un número entero'
        )
    return value


def _require_date(value, field_name):
    if isinstance(value, datetime) or not isinstance(value, date):
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} debe tener el formato AAAA-MM-DD'
        )
    return value


def _optional_datetime(value, field_name):
    if value is None:
        return None
    if not isinstance(value, datetime):
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} debe tener el formato AAAA-MM-DD HH:MM:SS'
        )
    return value


def _optional_text(value, field_name, max_length):
    if value is None:
        return None
    if not isinstance(value, str):
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} debe ser texto'
        )
    text = value.strip()
    if text == '':
        return None
    if len(text) > max_length:
        raise PlanillaEntregaServiceError(
            f'El campo {field_name} no debe superar {max_length} caracteres'
        )
    return text
