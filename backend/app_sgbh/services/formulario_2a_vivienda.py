from django.db import transaction
from django.db.models import Max

from ..db_router import DB_ALIAS
from ..models import (
    CondicionVivienda,
    Formulario2A,
    Formulario2AVivienda,
    MaterialPared,
    MaterialPiso,
    MaterialTecho,
    TipoUsoInstalacion,
)
from .formulario_2a import Formulario2AService, Formulario2AServiceError

_SMALLINT_MAX = 32767
_NUMERO_LOTE_MAX_LENGTH = 50


class Formulario2AViviendaServiceError(Exception):
    """Business rule violation for a vivienda operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


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

    @staticmethod
    def create(
        *,
        formulario_2a_id,
        numero_lote,
        tipo_uso_instalacion_id,
        tenencia_propia=None,
        condicion_vivienda_id=None,
        material_techo_id=None,
        material_pared_id=None,
        material_piso_id=None,
    ):
        """Insert one row in S43edan_formulario_2a_viviendas.

        The parent form must exist and still accept changes. numero_orden
        is the next order of that form: one more than its current maximum,
        or 1 when it has no viviendas. Catalog foreign keys must exist when
        they are sent. fecha_creacion uses the model default.
        """
        numero_lote = _require_numero_lote(numero_lote)

        with transaction.atomic(using=DB_ALIAS):
            formulario = _require_formulario(formulario_2a_id)
            _require_formulario_modificable(formulario)
            _require_catalogo(
                TipoUsoInstalacion,
                tipo_uso_instalacion_id,
                'El tipo de uso de instalación indicado no existe',
            )
            _require_catalogo_opcional(
                CondicionVivienda,
                condicion_vivienda_id,
                'La condición de vivienda indicada no existe',
            )
            _require_catalogo_opcional(
                MaterialTecho,
                material_techo_id,
                'El material de techo indicado no existe',
            )
            _require_catalogo_opcional(
                MaterialPared,
                material_pared_id,
                'El material de pared indicado no existe',
            )
            _require_catalogo_opcional(
                MaterialPiso,
                material_piso_id,
                'El material de piso indicado no existe',
            )
            numero_orden = _siguiente_numero_orden(formulario_2a_id)

            vivienda = Formulario2AVivienda(
                formulario_2a_id=formulario_2a_id,
                numero_orden=numero_orden,
                numero_lote=numero_lote,
                tenencia_propia=tenencia_propia,
                tipo_uso_instalacion_id=tipo_uso_instalacion_id,
                condicion_vivienda_id=condicion_vivienda_id,
                material_techo_id=material_techo_id,
                material_pared_id=material_pared_id,
                material_piso_id=material_piso_id,
            )
            vivienda.save()
            stored = Formulario2AVivienda.objects.select_related(
                'tipo_uso_instalacion',
                'condicion_vivienda',
                'material_techo',
                'material_pared',
                'material_piso',
            ).get(pk=vivienda.pk)
        return stored


def _require_numero_lote(numero_lote):
    if not isinstance(numero_lote, str):
        raise Formulario2AViviendaServiceError('El campo numero_lote debe ser texto')
    text = numero_lote.strip()
    if text == '':
        raise Formulario2AViviendaServiceError('El campo numero_lote es obligatorio')
    if len(text) > _NUMERO_LOTE_MAX_LENGTH:
        raise Formulario2AViviendaServiceError(
            'El campo numero_lote no debe superar 50 caracteres'
        )
    return text


def _require_formulario(formulario_2a_id):
    try:
        return (
            Formulario2A.objects.select_for_update().get(pk=formulario_2a_id)
        )
    except Formulario2A.DoesNotExist:
        raise Formulario2AViviendaServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ) from None


def _require_formulario_modificable(formulario):
    try:
        Formulario2AService.require_modificable(formulario)
    except Formulario2AServiceError as exc:
        raise Formulario2AViviendaServiceError(
            exc.message,
            conflict=exc.conflict,
            not_found=exc.not_found,
        ) from exc


def _require_catalogo(model, catalog_id, message):
    if not model.objects.filter(pk=catalog_id).exists():
        raise Formulario2AViviendaServiceError(message)


def _require_catalogo_opcional(model, catalog_id, message):
    if catalog_id is None:
        return
    _require_catalogo(model, catalog_id, message)


def _siguiente_numero_orden(formulario_2a_id):
    """Return the next numero_orden of one Formulario 2A.

    The caller must already hold the parent row lock so two inserts of the
    same form cannot take the same value.
    """
    max_orden = Formulario2AVivienda.objects.filter(
        formulario_2a_id=formulario_2a_id,
    ).aggregate(maximo=Max('numero_orden'))['maximo']
    numero_orden = 1 if max_orden is None else max_orden + 1
    if numero_orden > _SMALLINT_MAX:
        raise Formulario2AViviendaServiceError(
            'No se puede asignar otro número de orden en el formulario EDAN 2A',
            conflict=True,
        )
    return numero_orden
