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
