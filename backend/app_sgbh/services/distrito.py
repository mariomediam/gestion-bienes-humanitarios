from ..models import Distrito
from ..text_search import filter_text_like


class DistritoService:
    @staticmethod
    def search(
        departamento_id=None,
        provincia_id=None,
        distrito_id=None,
        distrito_nombre=None,
        f_activo=None,
    ):
        """Return rows from the DISTRITO view.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. distrito_nombre uses a
        case-insensitive partial match. The other filters are exact.
        With no filters, every row is returned. Ordered by distrito_id.
        """
        queryset = Distrito.objects.all()
        if departamento_id is not None:
            queryset = queryset.filter(departamento_id=departamento_id)
        if provincia_id is not None:
            queryset = queryset.filter(provincia_id=provincia_id)
        if distrito_id is not None:
            queryset = queryset.filter(distrito_id=distrito_id)
        if distrito_nombre is not None:
            queryset = filter_text_like(queryset, 'distrito_nombre', distrito_nombre)
        if f_activo is not None:
            queryset = queryset.filter(f_activo=f_activo)

        return queryset.order_by('distrito_id')
