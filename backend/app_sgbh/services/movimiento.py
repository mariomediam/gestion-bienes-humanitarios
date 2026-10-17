from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Prefetch, ProtectedError
from django.utils import timezone

from ..db_router import DB_ALIAS
from ..models import (
    Almacen,
    Bien,
    EstadoMovimiento,
    Movimiento,
    MovimientoDetalle,
    Personal,
    PlanillaEntrega,
    TipoMovimiento,
)
from ..text_search import filter_text_like

_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767
_INT_MIN = -2147483648
_INT_MAX = 2147483647
_CANTIDAD_MAXIMA = Decimal('1000000000000')
_NATURALEZA_ENTRADA = 'E'
_NATURALEZA_SALIDA = 'S'
_NATURALEZA_MIXTA = 'M'
_NATURALEZAS = (
    _NATURALEZA_ENTRADA,
    _NATURALEZA_SALIDA,
    _NATURALEZA_MIXTA,
)


class MovimientoServiceError(Exception):
    """Business rule violation for a warehouse movement operation."""

    def __init__(self, message, *, not_found=False, conflict=False):
        super().__init__(message)
        self.message = message
        self.not_found = not_found
        self.conflict = conflict


class MovimientoService:
    @staticmethod
    def search(
        movimiento_id=None,
        almacen_id=None,
        tipo_movimiento_id=None,
        estado_movimiento_id=None,
        movimiento_origen_id=None,
        fecha_desde=None,
        fecha_hasta=None,
        documento_referencia=None,
        destinatario=None,
        observacion=None,
        encargado_almacen_id=None,
        bien_nombre=None,
    ):
        """Return S43alm_movimientos rows using optional filters combined with AND.

        Joins almacén, tipo, estado and encargado. Each row keeps its
        S43alm_movimiento_detalle lines, with bien and unit of measure, under
        detalles. fecha_desde and fecha_hasta bound fecha_movimiento by
        calendar day, inclusive, because the column stores date and time.
        documento_referencia, destinatario, observacion and bien_nombre use a
        case-insensitive partial match. bien_nombre matches
        S43cat_bah_bienes.nombre of a detail line. The movement is included
        when at least one line matches, and detalles still lists every line.
        The other filters are exact. Ordered by fecha_movimiento descending.
        With no filters, every row is returned. The queryset is ready for
        MovimientoBusquedaSerializer.
        """
        queryset = Movimiento.objects.select_related(
            'almacen',
            'tipo_movimiento',
            'estado_movimiento',
            'encargado_almacen',
        ).prefetch_related(Prefetch('detalles', queryset=_detalles_busqueda()))
        if movimiento_id is not None:
            queryset = queryset.filter(movimiento_id=movimiento_id)
        if almacen_id is not None:
            queryset = queryset.filter(almacen_id=almacen_id)
        if tipo_movimiento_id is not None:
            queryset = queryset.filter(tipo_movimiento_id=tipo_movimiento_id)
        if estado_movimiento_id is not None:
            queryset = queryset.filter(estado_movimiento_id=estado_movimiento_id)
        if movimiento_origen_id is not None:
            queryset = queryset.filter(movimiento_origen_id=movimiento_origen_id)
        if fecha_desde is not None:
            queryset = queryset.filter(
                fecha_movimiento__gte=_inicio_de_dia(fecha_desde)
            )
        if fecha_hasta is not None:
            queryset = queryset.filter(
                fecha_movimiento__lt=_inicio_de_dia(fecha_hasta + timedelta(days=1))
            )
        if documento_referencia is not None:
            queryset = filter_text_like(
                queryset,
                'documento_referencia',
                documento_referencia,
            )
        if destinatario is not None:
            queryset = filter_text_like(queryset, 'destinatario', destinatario)
        if observacion is not None:
            queryset = filter_text_like(queryset, 'observacion', observacion)
        if encargado_almacen_id is not None:
            queryset = queryset.filter(encargado_almacen_id=encargado_almacen_id)
        if bien_nombre is not None:
            queryset = filter_text_like(
                queryset,
                'detalles__bien__nombre',
                bien_nombre,
            )
            queryset = queryset.distinct()

        return queryset.order_by('-fecha_movimiento')

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
    ):
        """Insert one S43alm_movimientos row and its detail rows.

        Header and details are written in one transaction. At least one
        detail is required. almacen, tipo de movimiento, estado, bien and
        encargado must exist and be active. The encargado must have
        es_encargado_almacen set. Quantity sign must match naturaleza:
        E positive, S negative and M either sign. A positive quantity cannot
        be devolvible. When the type requires an origin, movimiento_origen_id
        must reference an existing movement. fecha_creacion is the current
        time and fecha_modificacion stays null. c_usuari_login comes from
        the authenticated user.
        """
        header = _clean_header(
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
        )
        header['c_usuari_login'] = _require_token_login(c_usuari_login)
        lineas = _clean_detalles(detalles)

        with transaction.atomic(using=DB_ALIAS):
            _apply_header_rules(header, lineas)

            ahora = timezone.now()
            movimiento = Movimiento(
                almacen_id=header['almacen_id'],
                tipo_movimiento_id=header['tipo_movimiento_id'],
                estado_movimiento_id=header['estado_movimiento_id'],
                movimiento_origen_id=header['movimiento_origen_id'],
                fecha_movimiento=header['fecha_movimiento'],
                documento_referencia=header['documento_referencia'],
                fecha_documento=header['fecha_documento'],
                destinatario=header['destinatario'],
                observacion=header['observacion'],
                fecha_confirmacion=header['fecha_confirmacion'],
                encargado_almacen_id=header['encargado_almacen_id'],
                c_usuari_login=header['c_usuari_login'],
                fecha_creacion=ahora,
                fecha_modificacion=None,
            )
            try:
                movimiento.save()
            except IntegrityError:
                raise MovimientoServiceError(
                    'No se pudo registrar el movimiento de almacén'
                ) from None

            _insert_detalles(movimiento.pk, lineas, ahora)
            stored = _stored_movimiento(movimiento.pk)
        return stored

    @staticmethod
    def update(
        movimiento_id,
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
    ):
        """Replace one S43alm_movimientos row and all of its detail rows.

        The writable columns match create. c_usuari_login comes from the
        authenticated user and replaces the stored login. fecha_creacion
        stays as stored. fecha_modificacion is the current time. Existing
        detail rows are deleted and the sent lines are inserted with a new
        primary key and fecha_creacion. Rejected when any planilla BAH
        references this movement through movimiento_almacen_id.
        """
        header = _clean_header(
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
        )
        header['c_usuari_login'] = _require_token_login(c_usuari_login)
        lineas = _clean_detalles(detalles)

        with transaction.atomic(using=DB_ALIAS):
            try:
                movimiento = Movimiento.objects.get(pk=movimiento_id)
            except Movimiento.DoesNotExist:
                raise MovimientoServiceError(
                    'El movimiento de almacén indicado no existe',
                    not_found=True,
                ) from None

            if PlanillaEntrega.objects.filter(
                movimiento_almacen_id=movimiento.pk
            ).exists():
                raise MovimientoServiceError(
                    'No se puede modificar el movimiento de almacén porque '
                    'está vinculado a una planilla BAH',
                    conflict=True,
                )

            _apply_header_rules(header, lineas, movimiento_id=movimiento.pk)

            ahora = timezone.now()
            for field, value in header.items():
                setattr(movimiento, field, value)
            movimiento.fecha_modificacion = ahora
            try:
                movimiento.save(
                    update_fields=[*header.keys(), 'fecha_modificacion']
                )
            except IntegrityError:
                raise MovimientoServiceError(
                    'No se pudo modificar el movimiento de almacén'
                ) from None

            MovimientoDetalle.objects.filter(movimiento_id=movimiento.pk).delete()
            _insert_detalles(movimiento.pk, lineas, ahora)
            stored = _stored_movimiento(movimiento.pk)
        return stored

    @staticmethod
    def delete(movimiento_id):
        """Delete one S43alm_movimientos row and all of its detail rows.

        Detail rows are removed first because FK_alm_mov_det_movimiento
        does not cascade. Rejected when a planilla BAH references this
        movement through movimiento_almacen_id, or when another movement
        uses it as movimiento_origen_id. The checks and the deletes run
        in one transaction.
        """
        with transaction.atomic(using=DB_ALIAS):
            try:
                movimiento = Movimiento.objects.get(pk=movimiento_id)
            except Movimiento.DoesNotExist:
                raise MovimientoServiceError(
                    'El movimiento de almacén indicado no existe',
                    not_found=True,
                ) from None

            _reject_si_no_se_puede_eliminar(movimiento.pk)
            MovimientoDetalle.objects.filter(movimiento_id=movimiento.pk).delete()
            try:
                movimiento.delete()
            except ProtectedError:
                _reject_si_no_se_puede_eliminar(movimiento.pk)
                raise MovimientoServiceError(
                    'No se puede eliminar el movimiento de almacén porque '
                    'tiene registros asociados',
                    conflict=True,
                ) from None


def _reject_si_no_se_puede_eliminar(movimiento_id):
    if PlanillaEntrega.objects.filter(movimiento_almacen_id=movimiento_id).exists():
        raise MovimientoServiceError(
            'No se puede eliminar el movimiento de almacén porque '
            'está vinculado a una planilla BAH',
            conflict=True,
        )
    if Movimiento.objects.filter(movimiento_origen_id=movimiento_id).exists():
        raise MovimientoServiceError(
            'No se puede eliminar el movimiento de almacén porque '
            'es origen de otro movimiento',
            conflict=True,
        )


def _clean_header(
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
):
    return {
        'almacen_id': _require_int_id(almacen_id, 'almacen_id'),
        'tipo_movimiento_id': _require_smallint_id(
            tipo_movimiento_id,
            'tipo_movimiento_id',
        ),
        'estado_movimiento_id': _require_smallint_id(
            estado_movimiento_id,
            'estado_movimiento_id',
        ),
        'movimiento_origen_id': _optional_int_id(
            movimiento_origen_id,
            'movimiento_origen_id',
        ),
        'fecha_movimiento': _require_datetime(
            fecha_movimiento,
            'fecha_movimiento',
        ),
        'documento_referencia': _optional_text(
            documento_referencia,
            'documento_referencia',
            100,
        ),
        'fecha_documento': _optional_date(fecha_documento, 'fecha_documento'),
        'destinatario': _optional_text(destinatario, 'destinatario', 250),
        'observacion': _optional_text(observacion, 'observacion', 1000),
        'fecha_confirmacion': _optional_datetime(
            fecha_confirmacion,
            'fecha_confirmacion',
        ),
        'encargado_almacen_id': _require_smallint_id(
            encargado_almacen_id,
            'encargado_almacen_id',
        ),
    }


def _apply_header_rules(header, lineas, *, movimiento_id=None):
    """Check catalogs, origin, encargado, goods and quantity signs."""
    _require_activo(
        Almacen,
        header['almacen_id'],
        missing_message='El almacén indicado no existe',
        inactive_message='El almacén indicado no está activo',
    )
    tipo = _require_activo(
        TipoMovimiento,
        header['tipo_movimiento_id'],
        missing_message='El tipo de movimiento indicado no existe',
        inactive_message='El tipo de movimiento indicado no está activo',
    )
    _require_activo(
        EstadoMovimiento,
        header['estado_movimiento_id'],
        missing_message='El estado de movimiento indicado no existe',
        inactive_message='El estado de movimiento indicado no está activo',
    )
    origen_id = header['movimiento_origen_id']
    if movimiento_id is not None and origen_id == movimiento_id:
        raise MovimientoServiceError(
            'El movimiento de origen debe ser distinto de este movimiento'
        )
    _require_origen(tipo, origen_id)
    _require_encargado(header['encargado_almacen_id'])
    _require_bienes_activos(lineas)
    _require_signos_y_unicidad(lineas, tipo.naturaleza)


def _insert_detalles(movimiento_id, lineas, ahora):
    for linea in lineas:
        detalle = MovimientoDetalle(
            movimiento_id=movimiento_id,
            bien_id=linea['bien_id'],
            cantidad=linea['cantidad'],
            cantidad_texto=linea['cantidad_texto'],
            es_devolvible=linea['es_devolvible'],
            observacion=linea['observacion'],
            fecha_creacion=ahora,
        )
        try:
            detalle.save()
        except IntegrityError:
            raise MovimientoServiceError(
                'El bien ya está registrado con la misma modalidad '
                'de devolución en este movimiento',
                conflict=True,
            ) from None


def _stored_movimiento(movimiento_id):
    return Movimiento.objects.prefetch_related(
        Prefetch(
            'detalles',
            queryset=MovimientoDetalle.objects.order_by('movimiento_detalle_id'),
        )
    ).get(pk=movimiento_id)


def _require_token_login(value):
    """Login taken from the authenticated user, not from the request body."""
    login = str(value or '').strip()
    if login == '' or len(login) > 20:
        raise MovimientoServiceError('No se pudo identificar al usuario')
    return login


def _clean_detalles(detalles):
    if not isinstance(detalles, list):
        raise MovimientoServiceError('El campo detalles debe ser una lista')
    if len(detalles) == 0:
        raise MovimientoServiceError('Debe registrar al menos un detalle')

    lineas = []
    for item in detalles:
        if not isinstance(item, dict):
            raise MovimientoServiceError('Cada detalle debe ser un objeto')
        lineas.append(
            {
                'bien_id': _require_int_id(
                    item.get('bien_id', _MISSING),
                    'bien_id',
                ),
                'cantidad': _require_cantidad(item.get('cantidad', _MISSING)),
                'cantidad_texto': _optional_text(
                    item.get('cantidad_texto'),
                    'cantidad_texto',
                    30,
                ),
                'es_devolvible': _require_bool(
                    item.get('es_devolvible', _MISSING),
                    'es_devolvible',
                ),
                'observacion': _optional_text(
                    item.get('observacion'),
                    'observacion',
                    500,
                ),
            }
        )
    return lineas


class _Missing:
    pass


_MISSING = _Missing()


def _require_bienes_activos(lineas):
    ids = [linea['bien_id'] for linea in lineas]
    encontrados = {
        bien.bien_id: bien
        for bien in Bien.objects.filter(bien_id__in=ids)
    }
    for linea in lineas:
        bien = encontrados.get(linea['bien_id'])
        if bien is None:
            raise MovimientoServiceError('El bien indicado no existe')
        if not bien.esta_activo:
            raise MovimientoServiceError('El bien indicado no está activo')


def _require_signos_y_unicidad(lineas, naturaleza):
    codigo = str(naturaleza or '').strip().upper()
    if codigo not in _NATURALEZAS:
        raise MovimientoServiceError(
            'La naturaleza del tipo de movimiento no es válida'
        )

    vistos = set()
    for linea in lineas:
        _require_signo(linea['cantidad'], codigo)
        if linea['es_devolvible'] and linea['cantidad'] > 0:
            raise MovimientoServiceError(
                'Un detalle con cantidad positiva no puede ser devolvible'
            )
        clave = (linea['bien_id'], linea['es_devolvible'])
        if clave in vistos:
            raise MovimientoServiceError(
                'El bien ya está registrado con la misma modalidad '
                'de devolución en este movimiento',
                conflict=True,
            )
        vistos.add(clave)


def _require_signo(cantidad, naturaleza):
    if naturaleza == _NATURALEZA_ENTRADA and cantidad <= 0:
        raise MovimientoServiceError(
            'La cantidad debe ser positiva para un tipo de movimiento de entrada'
        )
    if naturaleza == _NATURALEZA_SALIDA and cantidad >= 0:
        raise MovimientoServiceError(
            'La cantidad debe ser negativa para un tipo de movimiento de salida'
        )


def _require_origen(tipo, movimiento_origen_id):
    if tipo.requiere_movimiento_origen and movimiento_origen_id is None:
        raise MovimientoServiceError(
            'El tipo de movimiento requiere un movimiento de origen'
        )
    if movimiento_origen_id is None:
        return
    origen = Movimiento.objects.filter(pk=movimiento_origen_id).first()
    if origen is None:
        raise MovimientoServiceError('El movimiento de origen indicado no existe')


def _require_encargado(personal_id):
    personal = Personal.objects.filter(pk=personal_id).first()
    if personal is None:
        raise MovimientoServiceError('El encargado de almacén indicado no existe')
    if not personal.esta_activo:
        raise MovimientoServiceError(
            'El encargado de almacén indicado no está activo'
        )
    if not personal.es_encargado_almacen:
        raise MovimientoServiceError(
            'El personal indicado no es encargado de almacén'
        )


def _require_activo(model, pk, *, missing_message, inactive_message):
    row = model.objects.filter(pk=pk).first()
    if row is None:
        raise MovimientoServiceError(missing_message)
    if not row.esta_activo:
        raise MovimientoServiceError(inactive_message)
    return row


def _require_cantidad(value):
    if value is _MISSING:
        raise MovimientoServiceError('El campo cantidad es obligatorio')
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise MovimientoServiceError(
            'El campo cantidad debe ser un número decimal'
        )
    if not value.is_finite():
        raise MovimientoServiceError(
            'El campo cantidad debe ser un número decimal'
        )
    if value == 0:
        raise MovimientoServiceError('El campo cantidad debe ser distinto de cero')
    exponent = value.as_tuple().exponent
    if (
        not isinstance(exponent, int)
        or exponent < -6
        or abs(value) >= _CANTIDAD_MAXIMA
    ):
        raise MovimientoServiceError(
            'El campo cantidad debe tener como máximo 18 dígitos y 6 decimales'
        )
    return value


def _require_bool(value, field_name):
    if value is _MISSING:
        raise MovimientoServiceError(f'El campo {field_name} es obligatorio')
    if not isinstance(value, bool):
        raise MovimientoServiceError(
            f'El campo {field_name} debe ser 1, 0, true o false'
        )
    return value


def _require_int_id(value, field_name):
    if value is _MISSING or value is None:
        raise MovimientoServiceError(f'El campo {field_name} es obligatorio')
    return _check_int(value, field_name, _INT_MIN, _INT_MAX)


def _require_smallint_id(value, field_name):
    if value is None:
        raise MovimientoServiceError(f'El campo {field_name} es obligatorio')
    return _check_int(value, field_name, _SMALLINT_MIN, _SMALLINT_MAX)


def _optional_int_id(value, field_name):
    if value is None:
        return None
    return _check_int(value, field_name, _INT_MIN, _INT_MAX)


def _check_int(value, field_name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int):
        raise MovimientoServiceError(
            f'El campo {field_name} debe ser un número entero'
        )
    if value < minimum or value > maximum:
        raise MovimientoServiceError(
            f'El campo {field_name} debe ser un número entero'
        )
    return value


def _detalles_busqueda():
    """Detail rows with bien and unit of measure, ordered by primary key."""
    return MovimientoDetalle.objects.select_related(
        'bien',
        'bien__unidad_medida',
    ).order_by('movimiento_detalle_id')


def _inicio_de_dia(fecha):
    """Aware midnight of fecha in the active timezone."""
    return timezone.make_aware(datetime.combine(fecha, time.min))


def _require_datetime(value, field_name):
    if not isinstance(value, datetime):
        raise MovimientoServiceError(
            f'El campo {field_name} debe tener el formato AAAA-MM-DD HH:MM:SS'
        )
    return value


def _optional_datetime(value, field_name):
    if value is None:
        return None
    return _require_datetime(value, field_name)


def _optional_date(value, field_name):
    if value is None:
        return None
    if isinstance(value, datetime) or not isinstance(value, date):
        raise MovimientoServiceError(
            f'El campo {field_name} debe tener el formato AAAA-MM-DD'
        )
    return value


def _optional_text(value, field_name, max_length):
    if value is None:
        return None
    if not isinstance(value, str):
        raise MovimientoServiceError(f'El campo {field_name} debe ser texto')
    text = value.strip()
    if text == '':
        return None
    if len(text) > max_length:
        raise MovimientoServiceError(
            f'El campo {field_name} no debe superar {max_length} caracteres'
        )
    return text
