from django.db import transaction
from django.db.models import ProtectedError

from ..db_router import DB_ALIAS
from ..models import Bien, CategoriaBien, MovimientoDetalle, ReglaEntrega, UnidadMedida
from ..text_search import filter_text_like

_NOMBRE_MAX_LENGTH = 250
_DESCRIPCION_MAX_LENGTH = 500
_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767
_UPDATABLE_FIELDS = (
    'categoria_bien_id',
    'unidad_medida_id',
    'nombre',
    'descripcion',
    'orden_impresion',
    'esta_activo',
    'visible_planilla',
)


class BienServiceError(Exception):
    """Business rule violation for a bien operation."""

    def __init__(self, message, *, not_found=False, conflict=False):
        super().__init__(message)
        self.message = message
        self.not_found = not_found
        self.conflict = conflict


class BienService:
    @staticmethod
    def search(
        bien_id=None,
        categoria_bien_id=None,
        unidad_medida_id=None,
        codigo=None,
        nombre=None,
    ):
        """Return S43cat_bah_bienes rows with category and unit of measure.

        Every filter is optional and combined with AND. When a filter is
        omitted, that column is not restricted. With no filters, every row
        is returned. bien_id, categoria_bien_id, unidad_medida_id and codigo
        are exact. nombre uses a case-insensitive LIKE. Spaces in the text
        become '%'. Ordered by nombre. The queryset is ready for
        BienBusquedaSerializer.
        """
        queryset = Bien.objects.select_related('categoria_bien', 'unidad_medida')
        if bien_id is not None:
            queryset = queryset.filter(bien_id=bien_id)
        if categoria_bien_id is not None:
            queryset = queryset.filter(categoria_bien_id=categoria_bien_id)
        if unidad_medida_id is not None:
            queryset = queryset.filter(unidad_medida_id=unidad_medida_id)
        if codigo is not None:
            queryset = queryset.filter(codigo=codigo)
        if nombre is not None:
            queryset = filter_text_like(queryset, 'nombre', nombre)

        return queryset.order_by('nombre')

    @staticmethod
    def update(bien_id, **changes):
        """Update the sent columns of one S43cat_bah_bienes row.

        Omitted columns stay as stored. codigo and bien_id are not editable.
        categoria_bien_id and unidad_medida_id must exist. An inactive
        category or unit is accepted. Rows already referenced by warehouse
        movements, delivery rules or other tables can still be updated.
        """
        if 'codigo' in changes:
            raise BienServiceError('El campo codigo no se puede modificar')

        cleaned = _clean_changes(changes)

        with transaction.atomic(using=DB_ALIAS):
            try:
                bien = Bien.objects.get(pk=bien_id)
            except Bien.DoesNotExist:
                raise BienServiceError(
                    'El bien indicado no existe',
                    not_found=True,
                ) from None

            if 'categoria_bien_id' in cleaned:
                _require_categoria_bien(cleaned['categoria_bien_id'])
            if 'unidad_medida_id' in cleaned:
                _require_unidad_medida(cleaned['unidad_medida_id'])

            update_fields = []
            for field in _UPDATABLE_FIELDS:
                if field in cleaned:
                    setattr(bien, field, cleaned[field])
                    update_fields.append(field)

            if update_fields:
                bien.save(update_fields=update_fields)

            stored = Bien.objects.select_related(
                'categoria_bien',
                'unidad_medida',
            ).get(pk=bien_id)
        return stored

    @staticmethod
    def delete(bien_id):
        """Delete one S43cat_bah_bienes row.

        Rejected when S43alm_movimiento_detalle already references that
        bien_id. Also rejected when S43cat_bah_reglas_entrega references
        it, because FK_cat_bah_regla_bien does not allow the delete.
        The check and the delete run in one transaction.
        """
        with transaction.atomic(using=DB_ALIAS):
            try:
                bien = Bien.objects.get(pk=bien_id)
            except Bien.DoesNotExist:
                raise BienServiceError(
                    'El bien indicado no existe',
                    not_found=True,
                ) from None

            _reject_if_referenced(bien_id)

            try:
                bien.delete()
            except ProtectedError:
                _reject_if_referenced(bien_id)
                raise BienServiceError(
                    'No se puede eliminar el bien porque tiene registros asociados',
                    conflict=True,
                ) from None


def _clean_changes(changes):
    cleaned = {}
    for field in _UPDATABLE_FIELDS:
        if field not in changes:
            continue
        value = changes[field]
        if field == 'nombre':
            value = _require_nombre(value)
        elif field == 'descripcion':
            value = _optional_descripcion(value)
        elif field == 'orden_impresion':
            value = _optional_orden(value)
        elif field in ('esta_activo', 'visible_planilla'):
            value = _require_bool(value, field)
        elif field == 'categoria_bien_id':
            value = _require_smallint_id(value, 'categoria_bien_id')
        elif field == 'unidad_medida_id':
            value = _require_smallint_id(value, 'unidad_medida_id')
        cleaned[field] = value
    return cleaned


def _require_nombre(value):
    if not isinstance(value, str):
        raise BienServiceError('El campo nombre debe ser texto')
    nombre = value.strip()
    if nombre == '':
        raise BienServiceError('El campo nombre es obligatorio')
    if len(nombre) > _NOMBRE_MAX_LENGTH:
        raise BienServiceError(
            'El campo nombre no debe superar 250 caracteres'
        )
    return nombre


def _optional_descripcion(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise BienServiceError('El campo descripcion debe ser texto')
    descripcion = value.strip()
    if descripcion == '':
        return None
    if len(descripcion) > _DESCRIPCION_MAX_LENGTH:
        raise BienServiceError(
            'El campo descripcion no debe superar 500 caracteres'
        )
    return descripcion


def _optional_orden(value):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise BienServiceError(
            'El campo orden_impresion debe ser un número entero'
        )
    if value < _SMALLINT_MIN or value > _SMALLINT_MAX:
        raise BienServiceError(
            'El campo orden_impresion debe ser un número entero'
        )
    if value < 1:
        raise BienServiceError('El campo orden_impresion debe ser mayor que 0')
    return value


def _require_bool(value, field_name):
    if not isinstance(value, bool):
        raise BienServiceError(
            f'El campo {field_name} debe ser 1, 0, true o false'
        )
    return value


def _require_smallint_id(value, field_name):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < _SMALLINT_MIN
        or value > _SMALLINT_MAX
    ):
        raise BienServiceError(
            f'El campo {field_name} debe ser un número entero'
        )
    return value


def _reject_if_referenced(bien_id):
    if MovimientoDetalle.objects.filter(bien_id=bien_id).exists():
        raise BienServiceError(
            'No se puede eliminar el bien porque tiene movimientos de almacén asociados',
            conflict=True,
        )
    if ReglaEntrega.objects.filter(bien_id=bien_id).exists():
        raise BienServiceError(
            'No se puede eliminar el bien porque tiene reglas de entrega asociadas',
            conflict=True,
        )


def _require_categoria_bien(categoria_bien_id):
    if not CategoriaBien.objects.filter(pk=categoria_bien_id).exists():
        raise BienServiceError('La categoría de bien indicada no existe')


def _require_unidad_medida(unidad_medida_id):
    if not UnidadMedida.objects.filter(pk=unidad_medida_id).exists():
        raise BienServiceError('La unidad de medida indicada no existe')
