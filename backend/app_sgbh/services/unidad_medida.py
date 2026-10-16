from ..models import UnidadMedida
from ..text_search import filter_text_like


class UnidadMedidaService:
    @staticmethod
    def list(
        unidad_medida_id=None,
        codigo=None,
        nombre=None,
        abreviatura=None,
        esta_activo=None,
    ):
        """List rows from S43cat_bah_unidades_medida ordered by nombre.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre and abreviatura use a
        case-insensitive LIKE pattern.
        """
        queryset = UnidadMedida.objects.all()
        if unidad_medida_id is not None:
            queryset = queryset.filter(unidad_medida_id=unidad_medida_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if abreviatura is not None:
            queryset = filter_text_like(queryset, 'abreviatura', abreviatura)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('nombre')
