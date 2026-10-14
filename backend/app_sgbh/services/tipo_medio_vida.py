from ..models import TipoMedioVida
from ..text_search import filter_text_like


class TipoMedioVidaService:
    @staticmethod
    def list(
        tipo_medio_vida_id=None,
        categoria_medio_vida_id=None,
        codigo_formulario=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_tipos_medios_vida ordered by id.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = TipoMedioVida.objects.all()
        if tipo_medio_vida_id is not None:
            queryset = queryset.filter(tipo_medio_vida_id=tipo_medio_vida_id)
        if categoria_medio_vida_id is not None:
            queryset = queryset.filter(
                categoria_medio_vida_id=categoria_medio_vida_id
            )
        if codigo_formulario is not None:
            queryset = queryset.filter(codigo_formulario=codigo_formulario)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('tipo_medio_vida_id')
