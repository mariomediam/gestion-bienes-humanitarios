from ..models import TipoUsoInstalacion
from ..text_search import filter_text_like


class TipoUsoInstalacionService:
    @staticmethod
    def list(
        tipo_uso_instalacion_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_tipos_uso_instalacion ordered by nombre.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = TipoUsoInstalacion.objects.all()
        if tipo_uso_instalacion_id is not None:
            queryset = queryset.filter(
                tipo_uso_instalacion_id=tipo_uso_instalacion_id
            )
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('nombre')
