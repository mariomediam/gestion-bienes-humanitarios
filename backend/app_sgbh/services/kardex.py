from datetime import datetime, time, timedelta

from django.utils import timezone

from ..models import AlmacenKardex


class AlmacenKardexService:
    @staticmethod
    def search(
        fecha_desde=None,
        fecha_hasta=None,
        almacen_id=None,
        estado_movimiento=None,
        bien_id=None,
    ):
        """Return S43vw_alm_kardex rows using optional filters combined with AND.

        fecha_desde and fecha_hasta bound fecha_movimiento by calendar day,
        inclusive, because the column stores date and time. almacen_id,
        estado_movimiento and bien_id are exact. estado_movimiento is the
        state code. With no filters, every row is returned. Ordered by
        fecha_movimiento and movimiento_detalle_id. The queryset is ready
        for AlmacenKardexBusquedaSerializer.
        """
        queryset = AlmacenKardex.objects.all()
        if fecha_desde is not None:
            queryset = queryset.filter(
                fecha_movimiento__gte=_inicio_de_dia(fecha_desde)
            )
        if fecha_hasta is not None:
            queryset = queryset.filter(
                fecha_movimiento__lt=_inicio_de_dia(fecha_hasta + timedelta(days=1))
            )
        if almacen_id is not None:
            queryset = queryset.filter(almacen_id=almacen_id)
        if estado_movimiento is not None:
            queryset = queryset.filter(estado_movimiento=estado_movimiento)
        if bien_id is not None:
            queryset = queryset.filter(bien_id=bien_id)

        return queryset.order_by('fecha_movimiento', 'movimiento_detalle_id')


def _inicio_de_dia(fecha):
    """Aware midnight of fecha in the active timezone."""
    return timezone.make_aware(datetime.combine(fecha, time.min))
