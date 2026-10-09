from django.db import transaction
from django.db.models import Max

from ..db_router import DB_ALIAS
from ..models import Formulario2A, Formulario2AFamilia, Formulario2AVivienda
from .formulario_2a import Formulario2AService, Formulario2AServiceError

_SMALLINT_MAX = 32767


class Formulario2AFamiliaServiceError(Exception):
    """Business rule violation for a familia operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class Formulario2AFamiliaService:
    @staticmethod
    def create(*, vivienda_id):
        """Insert one row in S43edan_formulario_2a_familias.

        The parent vivienda must exist and its Formulario 2A must still
        accept changes. numero_orden is the next order of that vivienda:
        one more than its current maximum, or 1 when it has no familias.
        fecha_creacion uses the model default.
        """
        with transaction.atomic(using=DB_ALIAS):
            vivienda = _require_vivienda(vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)
            numero_orden = _siguiente_numero_orden(vivienda_id)

            familia = Formulario2AFamilia(
                vivienda_id=vivienda_id,
                numero_orden=numero_orden,
            )
            familia.save()
            stored = Formulario2AFamilia.objects.get(pk=familia.pk)
        return stored


def _require_vivienda(vivienda_id):
    try:
        return Formulario2AVivienda.objects.select_for_update().get(pk=vivienda_id)
    except Formulario2AVivienda.DoesNotExist:
        raise Formulario2AFamiliaServiceError(
            'La vivienda indicada no existe',
            not_found=True,
        ) from None


def _require_formulario(formulario_2a_id):
    try:
        return Formulario2A.objects.select_for_update().get(pk=formulario_2a_id)
    except Formulario2A.DoesNotExist:
        raise Formulario2AFamiliaServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ) from None


def _require_formulario_modificable(formulario):
    try:
        Formulario2AService.require_modificable(formulario)
    except Formulario2AServiceError as exc:
        raise Formulario2AFamiliaServiceError(
            exc.message,
            conflict=exc.conflict,
            not_found=exc.not_found,
        ) from exc


def _siguiente_numero_orden(vivienda_id):
    """Return the next numero_orden of one vivienda.

    The caller must already hold the parent vivienda row lock so two inserts
    of the same vivienda cannot take the same value.
    """
    max_orden = Formulario2AFamilia.objects.filter(
        vivienda_id=vivienda_id,
    ).aggregate(maximo=Max('numero_orden'))['maximo']
    numero_orden = 1 if max_orden is None else max_orden + 1
    if numero_orden > _SMALLINT_MAX:
        raise Formulario2AFamiliaServiceError(
            'No se puede asignar otro número de orden en la vivienda',
            conflict=True,
        )
    return numero_orden
