"""Request-scoped values copied onto each audit log row."""

from contextvars import ContextVar

# Same width as c_usuari_login on the S43 tables.
MAX_LOGIN_LENGTH = 20

_audit_context: ContextVar[dict | None] = ContextVar(
    'app_audit_context',
    default=None,
)


def bind_audit_context(data):
    """Remember the dict that django-auditlog will copy onto the log row."""
    return _audit_context.set(data)


def reset_audit_context(token):
    _audit_context.reset(token)


def current_audit_context():
    return _audit_context.get()


def set_audit_login(login):
    """Store the institutional login of the request that is writing."""
    context = _audit_context.get()
    if context is None:
        return
    value = str(login or '').strip()
    if len(value) > MAX_LOGIN_LENGTH:
        value = ''
    context['c_usuari_login'] = value
