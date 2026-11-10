from django.db.models.signals import pre_save
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from app_auth.authentication import ExternalUser
from app_audit.context import current_audit_context
from app_audit.middleware import AuditContextMiddleware
from app_audit.models import AuditLogEntry
from auditlog.context import set_extra_data
from auditlog.registry import auditlog
from app_sgbh.models import (
    Bien,
    Emergencia,
    Formulario2A,
    Formulario2AArchivo,
    Formulario2AFamilia,
    Formulario2AIntegrante,
    Formulario2AMedioVida,
    Formulario2AVivienda,
    Movimiento,
    MovimientoDetalle,
    Persona,
    PlanillaEntrega,
)


TRACKED_MODELS = (
    Persona,
    Emergencia,
    Formulario2A,
    Formulario2AVivienda,
    Formulario2AFamilia,
    Formulario2AIntegrante,
    Formulario2AMedioVida,
    Formulario2AArchivo,
    PlanillaEntrega,
    Movimiento,
    MovimientoDetalle,
    Bien,
)


def test_tracked_models_are_registered():
    for model in TRACKED_MODELS:
        assert auditlog.contains(model), model.__name__


def test_middleware_keeps_ip_until_the_view_finishes():
    captured = {}

    def view(request):
        captured['context'] = dict(current_audit_context())
        from django.http import HttpResponse
        return HttpResponse('ok')

    request = APIRequestFactory().get(
        '/probe/',
        HTTP_X_FORWARDED_FOR='203.0.113.8, 10.0.0.1',
    )
    response = AuditContextMiddleware(view)(request)

    assert response.status_code == 200
    assert captured['context']['remote_addr'] == '203.0.113.8'
    assert captured['context']['c_usuari_login'] == ''
    assert current_audit_context() is None


def test_authenticated_view_stores_the_token_login():
    captured = {}

    class ProbeView(APIView):
        authentication_classes = []
        permission_classes = []

        def get(self, request):
            captured['login'] = current_audit_context()['c_usuari_login']
            captured['ip'] = current_audit_context()['remote_addr']
            return Response(status=204)

    request = APIRequestFactory().get('/probe/', REMOTE_ADDR='192.168.1.10')
    force_authenticate(request, user=ExternalUser(login=' mmedina ', nombre='Mario'))
    response = AuditContextMiddleware(ProbeView.as_view())(request)

    assert response.status_code == 204
    assert captured['login'] == 'mmedina'
    assert captured['ip'] == '192.168.1.10'


def test_login_longer_than_the_column_is_not_stored():
    captured = {}

    class ProbeView(APIView):
        authentication_classes = []
        permission_classes = []

        def get(self, request):
            captured['login'] = current_audit_context()['c_usuari_login']
            return Response(status=204)

    request = APIRequestFactory().get('/probe/')
    force_authenticate(request, user=ExternalUser(login='a' * 21, nombre='Mario'))
    AuditContextMiddleware(ProbeView.as_view())(request)

    assert captured['login'] == ''


def test_log_entry_receives_login_and_ip_before_save():
    entry = AuditLogEntry(action=AuditLogEntry.Action.CREATE, object_pk='1', object_repr='row')

    with set_extra_data({'c_usuari_login': 'mmedina', 'remote_addr': '10.1.1.1'}):
        pre_save.send(sender=AuditLogEntry, instance=entry)

    assert entry.c_usuari_login == 'mmedina'
    assert entry.remote_addr == '10.1.1.1'
    assert entry.actor is None
