from ..models import MaterialPared
from ..text_search import filter_text_like


class MaterialParedService:
    @staticmethod
    def list(
        material_pared_id=None,
        codigo_formulario=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_materiales_pared ordered by nombre.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = MaterialPared.objects.all()
        if material_pared_id is not None:
            queryset = queryset.filter(material_pared_id=material_pared_id)
        if codigo_formulario is not None:
            queryset = queryset.filter(codigo_formulario=codigo_formulario)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('nombre')
