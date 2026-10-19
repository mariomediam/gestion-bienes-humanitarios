from django.db.models import CharField, F, Func, OuterRef, Prefetch, Subquery

from ..models import Distrito, MovimientoDetalle, PlanillaEntrega
from ..text_search import filter_text_like, text_like_pattern


class MovimientoPlanillaBahService:
    @staticmethod
    def search(
        planilla_entrega_id=None,
        movimiento_id=None,
        numero_planilla=None,
        anio_planilla=None,
        codigo_sinpad=None,
        barrio_sector_urbanizacion=None,
        fecha_desde=None,
        fecha_hasta=None,
        documento_referencia=None,
        integrante_receptor_nombre=None,
        bien_nombre=None,
    ):
        """Return planillas BAH linked to S43alm_movimientos.

        The base query is the inner join
        S43alm_movimientos.movimiento_id =
        S43bah_planilla_entrega.movimiento_almacen_id. Planillas without a
        movement are excluded. Every filter is optional and combined with
        AND. With no filters, every linked row is returned.

        planilla_entrega_id, movimiento_id, numero_planilla, anio_planilla
        and codigo_sinpad are exact. fecha_desde and fecha_hasta bound
        fecha_entrega, inclusive. barrio_sector_urbanizacion,
        documento_referencia, integrante_receptor_nombre and bien_nombre
        use a case-insensitive partial match. integrante_receptor_nombre
        matches apellido_paterno + ' ' + apellido_materno + ' ' + nombres.
        bien_nombre matches S43cat_bah_bienes.nombre on the movement lines.
        Ordered by fecha_movimiento descending. Each row keeps its
        S43alm_movimiento_detalle lines under detalles. The queryset is
        ready for MovimientoPlanillaBahBusquedaSerializer.
        """
        queryset = _planillas_busqueda()
        if planilla_entrega_id is not None:
            queryset = queryset.filter(planilla_entrega_id=planilla_entrega_id)
        if movimiento_id is not None:
            queryset = queryset.filter(movimiento_almacen_id=movimiento_id)
        if numero_planilla is not None:
            queryset = queryset.filter(numero_planilla=numero_planilla)
        if anio_planilla is not None:
            queryset = queryset.filter(anio_planilla=anio_planilla)
        if codigo_sinpad is not None:
            queryset = queryset.filter(
                integrante_receptor__familia__vivienda__formulario_2a__emergencia__codigo_sinpad=(
                    codigo_sinpad
                ),
            )
        if barrio_sector_urbanizacion is not None:
            queryset = filter_text_like(
                queryset,
                'integrante_receptor__familia__vivienda__formulario_2a__barrio_sector_urbanizacion',
                barrio_sector_urbanizacion,
            )
        if fecha_desde is not None:
            queryset = queryset.filter(fecha_entrega__gte=fecha_desde)
        if fecha_hasta is not None:
            queryset = queryset.filter(fecha_entrega__lte=fecha_hasta)
        if documento_referencia is not None:
            queryset = filter_text_like(
                queryset,
                'movimiento_almacen__documento_referencia',
                documento_referencia,
            )
        if integrante_receptor_nombre is not None:
            queryset = queryset.alias(
                integrante_receptor_nombre=_NombreReceptor(),
            ).filter(
                integrante_receptor_nombre__ilike_pattern=text_like_pattern(
                    integrante_receptor_nombre
                ),
            )
        if bien_nombre is not None:
            queryset = filter_text_like(
                queryset,
                'movimiento_almacen__detalles__bien__nombre',
                bien_nombre,
            )
            queryset = queryset.distinct()

        return queryset.order_by('-movimiento_almacen__fecha_movimiento')


def _planillas_busqueda():
    """Planillas with a warehouse movement, location and detail lines.

    distrito_nombre comes from DISTRITO matched by the three ubigeo codes
    of the receptor's formulario. Detail lines stay on the movement.
    """
    distrito_nombre = Distrito.objects.filter(
        departamento_id=OuterRef(
            'integrante_receptor__familia__vivienda__formulario_2a__departamento_id'
        ),
        provincia_id=OuterRef(
            'integrante_receptor__familia__vivienda__formulario_2a__provincia_id'
        ),
        distrito_id=OuterRef(
            'integrante_receptor__familia__vivienda__formulario_2a__distrito_id'
        ),
    ).values('distrito_nombre')[:1]
    return (
        PlanillaEntrega.objects.filter(movimiento_almacen__isnull=False)
        .select_related(
            'movimiento_almacen',
            'movimiento_almacen__almacen',
            'movimiento_almacen__tipo_movimiento',
            'movimiento_almacen__estado_movimiento',
            'movimiento_almacen__encargado_almacen',
            'integrante_receptor',
            'integrante_receptor__persona',
            'integrante_receptor__familia',
            'integrante_receptor__familia__vivienda',
            'integrante_receptor__familia__vivienda__formulario_2a',
            'integrante_receptor__familia__vivienda__formulario_2a__emergencia',
        )
        .annotate(distrito_nombre=Subquery(distrito_nombre, output_field=CharField()))
        .prefetch_related(
            Prefetch(
                'movimiento_almacen__detalles',
                queryset=_detalles_busqueda(),
            )
        )
    )


def _detalles_busqueda():
    """Detail rows with bien and unit of measure, ordered by primary key."""
    return MovimientoDetalle.objects.select_related(
        'bien',
        'bien__unidad_medida',
    ).order_by('movimiento_detalle_id')


class _NombreReceptor(Func):
    """apellido_paterno + ' ' + apellido_materno + ' ' + nombres.

    The + operator stays compatible with SQL Server 2008 R2. CONCAT() does
    not exist in that version.
    """

    template = '%(expressions)s'
    arg_joiner = " + ' ' + "
    output_field = CharField()

    def __init__(self):
        super().__init__(
            F('integrante_receptor__persona__apellido_paterno'),
            F('integrante_receptor__persona__apellido_materno'),
            F('integrante_receptor__persona__nombres'),
        )
