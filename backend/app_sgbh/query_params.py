"""Shared parsers for optional query parameters."""

_TRUE_VALUES = {'1', 'true'}
_FALSE_VALUES = {'0', 'false'}


def parse_esta_activo(raw_value):
    """Parse the optional esta_activo query param.

    Returns (value, error_message). value is True, False or None.
    None means the filter was omitted.
    """
    if raw_value is None or raw_value == '':
        return None, None

    normalized = str(raw_value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True, None
    if normalized in _FALSE_VALUES:
        return False, None

    return None, 'El filtro esta_activo debe ser 1, 0, true o false'


_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


def parse_estado_registro_id(raw_value):
    """Parse the optional estado_registro_id query param.

    Returns (value, error_message). value is an int or None.
    None means the filter was omitted.
    """
    if raw_value is None or str(raw_value).strip() == '':
        return None, None

    normalized = str(raw_value).strip()
    try:
        value = int(normalized)
    except (TypeError, ValueError):
        return None, 'El filtro estado_registro_id debe ser un número entero'

    if value < _SMALLINT_MIN or value > _SMALLINT_MAX:
        return None, 'El filtro estado_registro_id debe ser un número entero'

    return value, None
