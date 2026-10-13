from ..models import TipoDocumento
from ..text_search import filter_text_like


class TipoDocumentoService:
    @staticmethod
    def list(
        tipo_documento_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    ):
        """List rows from S43cat_tipos_documento ordered by tipo_documento_id.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. nombre uses a
        case-insensitive LIKE pattern.
        """
        queryset = TipoDocumento.objects.all()
        if tipo_documento_id is not None:
            queryset = queryset.filter(tipo_documento_id=tipo_documento_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by('tipo_documento_id')
