from ..models import Personal


class PersonalService:
    @staticmethod
    def search(
        personal_id=None,
        es_evaluador_edan=None,
        es_encargado_almacen=None,
        esta_activo=None,
    ):
        """Return rows from S43bah_personal.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. With no filters, every row
        is returned.
        """
        queryset = Personal.objects.all()
        if personal_id is not None:
            queryset = queryset.filter(personal_id=personal_id)
        if es_evaluador_edan is not None:
            queryset = queryset.filter(es_evaluador_edan=es_evaluador_edan)
        if es_encargado_almacen is not None:
            queryset = queryset.filter(es_encargado_almacen=es_encargado_almacen)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)

        return queryset.order_by(
            'apellido_paterno',
            'apellido_materno',
            'nombres',
            'personal_id',
        )
