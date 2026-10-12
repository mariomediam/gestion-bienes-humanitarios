from ..models import TipoDiscapacidad
from ..text_search import filter_text_like


class TipoDiscapacidadService:
    @staticmethod
    def list(
        tipo_discapacidad_id=None,
        codigo_formulario=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_tipos_discapacidad ordered by tipo_discapacidad_id.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = TipoDiscapacidad.objects.all()
        if tipo_discapacidad_id is not None:
            queryset = queryset.filter(tipo_discapacidad_id=tipo_discapacidad_id)
        if codigo_formulario is not None:
            queryset = queryset.filter(codigo_formulario=codigo_formulario)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('tipo_discapacidad_id')
