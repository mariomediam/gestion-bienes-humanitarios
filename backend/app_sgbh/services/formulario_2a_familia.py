from django.db import transaction
from django.db.models import Max, ProtectedError

from ..db_router import DB_ALIAS
from ..models import (
    Formulario2A,
    Formulario2AFamilia,
    Formulario2AIntegrante,
    Formulario2AVivienda,
)
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
    def search(familia_id=None, vivienda_id=None, formulario_2a_id=None):
        """Return familia rows using optional filters combined with AND.

        Filters are exact. With no filters, every row is returned.
        formulario_2a_id comes from the vivienda parent.
        Ordered by the vivienda numero_orden and then the familia numero_orden.
        The queryset is ready for FamiliaBusquedaSerializer.
        """
        queryset = Formulario2AFamilia.objects.select_related(
            'vivienda',
            'vivienda__formulario_2a',
        )
        if familia_id is not None:
            queryset = queryset.filter(familia_id=familia_id)
        if vivienda_id is not None:
            queryset = queryset.filter(vivienda_id=vivienda_id)
        if formulario_2a_id is not None:
            queryset = queryset.filter(
                vivienda__formulario_2a_id=formulario_2a_id,
            )

        return queryset.order_by('vivienda__numero_orden', 'numero_orden')

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

    @staticmethod
    def delete(familia_id):
        """Delete one S43edan_formulario_2a_familias row.

        The familia, its vivienda and the parent Formulario 2A must exist,
        and the form must still accept changes. Also rejected when at least
        one integrante belongs to that familia.
        """
        with transaction.atomic(using=DB_ALIAS):
            familia = _require_familia(familia_id)
            vivienda = _require_vivienda(familia.vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)
            if _tiene_integrantes(familia_id):
                raise Formulario2AFamiliaServiceError(
                    'No se puede eliminar la familia. Primero debe eliminar los integrantes de la familia',
                    conflict=True,
                )

            try:
                familia.delete()
            except ProtectedError:
                raise Formulario2AFamiliaServiceError(
                    'No se puede eliminar la familia porque tiene registros asociados',
                    conflict=True,
                ) from None


def _require_familia(familia_id):
    try:
        return Formulario2AFamilia.objects.select_for_update().get(pk=familia_id)
    except Formulario2AFamilia.DoesNotExist:
        raise Formulario2AFamiliaServiceError(
            'La familia indicada no existe',
            not_found=True,
        ) from None


def _tiene_integrantes(familia_id):
    """True when any integrante belongs to this familia."""
    return Formulario2AIntegrante.objects.filter(familia_id=familia_id).exists()


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
