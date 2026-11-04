from datetime import datetime, time, timedelta

from django.db.models import Case, CharField, F, Func, When
from django.utils import timezone

from ..models import Movimiento
from ..text_search import filter_text_like

_CODIGO_DEVOLUCION = 'DEVOLUCION'
_CODIGO_ENTREGA_BAH = 'ENTREGA_BAH'


class MovimientoDevolucionService:
    @staticmethod
    def search(
        movimiento_id=None,
        almacen_id=None,
        estado_movimiento_id=None,
        movimiento_origen_id=None,
        fecha_movimiento=None,
        documento_referencia=None,
        fecha_documento_desde=None,
        fecha_documento_hasta=None,
        documento_origen_referencia=None,
    ):
        """Return S43alm_movimientos rows whose type code is DEVOLUCION.

        The query keeps the left joins of the devolución search: almacén,
        type, state, origin movement, origin type, planilla of that origin,
        detail, bien and unit of measure. A movement without detail lines
        stays in the result, with null detail columns. Several planillas
        for the same origin multiply rows the same way the joins do.

        documento_origen_referencia is numero_planilla + '-' + anio_planilla
        when the origin type code is ENTREGA_BAH. Otherwise it is the origin
        documento_referencia. Both numbers are CONVERT(varchar(5), ...),
        joined with +, so the expression stays valid on SQL Server 2008 R2.

        Every filter is optional and combined with AND. movimiento_id,
        almacen_id, estado_movimiento_id and movimiento_origen_id are exact.
        fecha_movimiento matches that calendar day, because the column stores
        date and time. fecha_documento_desde and fecha_documento_hasta bound
        fecha_documento, inclusive. documento_referencia and
        documento_origen_referencia use a case-insensitive partial match.
        With no filters, every DEVOLUCION row is returned. Ordered by
        fecha_movimiento descending and movimiento_detalle_id. The queryset
        is ready for MovimientoDevolucionBusquedaSerializer.
        """
        queryset = (
            Movimiento.objects.filter(tipo_movimiento__codigo=_CODIGO_DEVOLUCION)
            .select_related('almacen', 'tipo_movimiento', 'estado_movimiento')
            .annotate(**_anotaciones_busqueda())
        )
        if movimiento_id is not None:
            queryset = queryset.filter(movimiento_id=movimiento_id)
        if almacen_id is not None:
            queryset = queryset.filter(almacen_id=almacen_id)
        if estado_movimiento_id is not None:
            queryset = queryset.filter(estado_movimiento_id=estado_movimiento_id)
        if movimiento_origen_id is not None:
            queryset = queryset.filter(movimiento_origen_id=movimiento_origen_id)
        if fecha_movimiento is not None:
            queryset = queryset.filter(
                fecha_movimiento__gte=_inicio_de_dia(fecha_movimiento),
                fecha_movimiento__lt=_inicio_de_dia(
                    fecha_movimiento + timedelta(days=1)
                ),
            )
        if documento_referencia is not None:
            queryset = filter_text_like(
                queryset,
                'documento_referencia',
                documento_referencia,
            )
        if fecha_documento_desde is not None:
            queryset = queryset.filter(fecha_documento__gte=fecha_documento_desde)
        if fecha_documento_hasta is not None:
            queryset = queryset.filter(fecha_documento__lte=fecha_documento_hasta)
        if documento_origen_referencia is not None:
            queryset = filter_text_like(
                queryset,
                'documento_origen_referencia',
                documento_origen_referencia,
            )

        return queryset.order_by(
            '-fecha_movimiento',
            'detalles__movimiento_detalle_id',
        )


def _anotaciones_busqueda():
    """Columns produced by the left joins that are not on S43alm_movimientos."""
    return {
        'tipo_movimiento_origen_nombre': F(
            'movimiento_origen__tipo_movimiento__nombre'
        ),
        'documento_origen_referencia': Case(
            When(
                movimiento_origen__tipo_movimiento__codigo=_CODIGO_ENTREGA_BAH,
                then=_NumeroAnioPlanilla(),
            ),
            default=F('movimiento_origen__documento_referencia'),
            output_field=CharField(),
        ),
        'movimiento_detalle_id': F('detalles__movimiento_detalle_id'),
        'bien_id': F('detalles__bien_id'),
        'cantidad': F('detalles__cantidad'),
        'cantidad_texto': F('detalles__cantidad_texto'),
        'es_devolvible': F('detalles__es_devolvible'),
        'movimiento_detalle_observacion': F('detalles__observacion'),
        'categoria_bien_id': F('detalles__bien__categoria_bien_id'),
        'unidad_medida_id': F('detalles__bien__unidad_medida_id'),
        'bien_codigo': F('detalles__bien__codigo'),
        'bien_nombre': F('detalles__bien__nombre'),
        'unidad_medida_codigo': F('detalles__bien__unidad_medida__codigo'),
        'unidad_medida_nombre': F('detalles__bien__unidad_medida__nombre'),
        'unidad_medida_abreviatura': F(
            'detalles__bien__unidad_medida__abreviatura'
        ),
    }


class _NumeroAnioPlanilla(Func):
    """CONVERT(varchar(5), numero) + '-' + CONVERT(varchar(5), anio).

    CAST(... AS nvarchar) is not the search SQL. CONVERT to varchar(5)
    and the + operator stay valid on SQL Server 2008 R2.
    """

    template = 'CONVERT(varchar(5), %(expressions)s)'
    arg_joiner = ") + '-' + CONVERT(varchar(5), "
    output_field = CharField()

    def __init__(self):
        super().__init__(
            F('movimiento_origen__planillas_entrega__numero_planilla'),
            F('movimiento_origen__planillas_entrega__anio_planilla'),
        )


def _inicio_de_dia(fecha):
    """Aware midnight of fecha in the active timezone."""
    return timezone.make_aware(datetime.combine(fecha, time.min))
