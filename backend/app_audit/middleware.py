"""Open an audit context for the request and keep the client IP."""

from auditlog.cid import set_cid
from auditlog.context import set_extra_data

from app_audit.context import bind_audit_context, reset_audit_context


class AuditContextMiddleware:
    """Keep django-auditlog's context open until the response is finished.

    The institutional login is filled later, when DRF has authenticated the
    request. The IP is taken here, with the same proxy header the package uses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_cid(request)
        context_data = {
            'c_usuari_login': '',
            'remote_addr': _client_ip(request),
        }
        token = bind_audit_context(context_data)
        try:
            with set_extra_data(context_data=context_data):
                return self.get_response(request)
        finally:
            reset_audit_context(token)


def _client_ip(request):
    """Return the client IP, using the first X-Forwarded-For hop when present."""
    forwarded = request.headers.get('X-Forwarded-For')
    if not forwarded:
        return request.META.get('REMOTE_ADDR') or None

    remote_addr = forwarded.split(',')[0].strip()
    if '.' in remote_addr and ':' in remote_addr:
        remote_addr = remote_addr.split(':')[0]
    elif remote_addr.startswith('['):
        remote_addr = remote_addr[1:].split(']')[0]
    return remote_addr or None
