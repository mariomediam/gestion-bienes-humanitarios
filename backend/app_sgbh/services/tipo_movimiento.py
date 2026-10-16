from ..models import TipoMovimiento
from ..text_search import filter_text_like


class TipoMovimientoService:
    @staticmethod
    def list(
        tipo_movimiento_id=None,
        codigo=None,
        nombre=None,
        naturaleza=None,
        requiere_movimiento_origen=None,
        esta_activo=None,
    ):
        """List rows from S43cat_alm_tipos_movimiento ordered by nombre.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = TipoMovimiento.objects.all()
        if tipo_movimiento_id is not None:
            queryset = queryset.filter(tipo_movimiento_id=tipo_movimiento_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if naturaleza is not None:
            queryset = queryset.filter(naturaleza=naturaleza)
        if requiere_movimiento_origen is not None:
            queryset = queryset.filter(
                requiere_movimiento_origen=requiere_movimiento_origen
            )
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('nombre')
