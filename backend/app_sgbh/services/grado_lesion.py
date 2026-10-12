from ..models import GradoLesion
from ..text_search import filter_text_like


class GradoLesionService:
    @staticmethod
    def list(
        grado_lesion_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_grados_lesion ordered by grado_lesion_id.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = GradoLesion.objects.all()
        if grado_lesion_id is not None:
            queryset = queryset.filter(grado_lesion_id=grado_lesion_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('grado_lesion_id')
