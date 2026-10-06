from ..models import Formulario2AVivienda


class Formulario2AViviendaService:
    @staticmethod
    def search(vivienda_id=None, formulario_2a_id=None):
        """Return vivienda rows using optional filters combined with AND.

        Both filters are exact. With no filters, every row is returned.
        Ordered by vivienda_id. Catalog names come from the related rows.
        The queryset is ready for ViviendaBusquedaSerializer.
        """
        queryset = Formulario2AVivienda.objects.select_related(
            'tipo_uso_instalacion',
            'condicion_vivienda',
            'material_techo',
            'material_pared',
            'material_piso',
        )
        if vivienda_id is not None:
            queryset = queryset.filter(vivienda_id=vivienda_id)
        if formulario_2a_id is not None:
            queryset = queryset.filter(formulario_2a_id=formulario_2a_id)

        return queryset.order_by('vivienda_id')
