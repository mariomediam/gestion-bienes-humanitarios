from decimal import Decimal

from django.db.models import DecimalField, F, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Abs, Coalesce

from ..models import MovimientoDetalle

_CANTIDAD = DecimalField(max_digits=18, decimal_places=6)


class MovimientoCantidadesSalidaService:
    @staticmethod
    def list(movimiento_id):
        """Return salida quantities and the entradas posted against them.

        One row per S43alm_movimiento_detalle line of movimiento_id when
        S43cat_alm_tipos_movimiento.naturaleza is S. cantidad_salida is
        ABS(cantidad) of that line. cantidad_entrada is the sum of
        ABS(cantidad) of detail lines whose movement has naturaleza E and
        movimiento_origen_id equal to movimiento_id, grouped by bien_id.
        A bien without entradas returns 0. bien_nombre is
        S43cat_bah_bienes.nombre and abreviatura_nombre is
        S43cat_bah_unidades_medida.abreviatura. A movement that is missing
        or is not naturaleza S returns no rows. The queryset yields dicts
        ready for MovimientoCantidadesSalidaSerializer.
        """
        cantidad_entrada = (
            MovimientoDetalle.objects.filter(
                bien_id=OuterRef('bien_id'),
                movimiento__movimiento_origen_id=movimiento_id,
                movimiento__tipo_movimiento__naturaleza='E',
            )
            .values('bien_id')
            .annotate(total=Sum(Abs('cantidad')))
            .values('total')
        )
        return (
            MovimientoDetalle.objects.filter(
                movimiento_id=movimiento_id,
                movimiento__tipo_movimiento__naturaleza='S',
            )
            .annotate(
                cantidad_salida=Abs('cantidad'),
                cantidad_entrada=Coalesce(
                    Subquery(cantidad_entrada, output_field=_CANTIDAD),
                    Value(Decimal('0')),
                    output_field=_CANTIDAD,
                ),
                bien_nombre=F('bien__nombre'),
                abreviatura_nombre=F('bien__unidad_medida__abreviatura'),
            )
            .values(
                'bien_id',
                'bien_nombre',
                'abreviatura_nombre',
                'cantidad_salida',
                'cantidad_entrada',
            )
        )
