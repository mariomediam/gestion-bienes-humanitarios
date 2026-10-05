from datetime import date, time
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import EmergenciaCreateSerializer, first_error_message
from app_sgbh.services.emergencia import EmergenciaService, EmergenciaServiceError
from app_sgbh.views.emergencia_view import EmergenciaListView


def _parse_crear(data):
    serializer = EmergenciaCreateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'numero_evaluacion': 'EV-001',
        'codigo_sinpad': 'SIN-001',
        'tipo_peligro_id': 3,
        'fecha_emergencia': '2026-10-01',
    }
    data.update(overrides)
    return data


def test_parse_crear_accepts_required_fields_and_defaults():
    parsed, error = _parse_crear(_body())

    assert error is None
    assert parsed == {
        'numero_evaluacion': 'EV-001',
        'codigo_sinpad': 'SIN-001',
        'tipo_peligro_id': 3,
        'fecha_emergencia': date(2026, 10, 1),
        'hora_ocurrencia_estimada': None,
        'esta_activo': True,
    }


def test_parse_crear_trims_text_and_reads_optional_fields():
    parsed, error = _parse_crear(
        _body(
            numero_evaluacion='  EV-002  ',
            codigo_sinpad='  sin-002  ',
            tipo_peligro_id='4',
            hora_ocurrencia_estimada='08:15',
            esta_activo=False,
        )
    )

    assert error is None
    assert parsed['numero_evaluacion'] == 'EV-002'
    assert parsed['codigo_sinpad'] == 'sin-002'
    assert parsed['tipo_peligro_id'] == 4
    assert parsed['hora_ocurrencia_estimada'] == time(8, 15)
    assert parsed['esta_activo'] is False


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('numero_evaluacion', '   ', 'numero_evaluacion es obligatorio'),
        ('codigo_sinpad', '', 'codigo_sinpad es obligatorio'),
        ('codigo_sinpad', 'X' * 31, 'codigo_sinpad no debe superar 30'),
        ('tipo_peligro_id', None, 'tipo_peligro_id es obligatorio'),
        ('tipo_peligro_id', '3.5', 'tipo_peligro_id debe ser un número entero'),
        ('fecha_emergencia', '01/10/2026', 'fecha_emergencia debe tener el formato'),
        ('hora_ocurrencia_estimada', '8pm', 'hora_ocurrencia_estimada debe tener el formato'),
        ('esta_activo', 'si', 'esta_activo debe ser 1, 0, true o false'),
    ],
)
def test_parse_crear_rejects_invalid_fields(field, value, message):
    _parsed, error = _parse_crear(_body(**{field: value}))

    assert error is not None
    assert message in error


def test_create_rejects_blank_codigo_sinpad_before_saving():
    with pytest.raises(EmergenciaServiceError) as exc:
        EmergenciaService.create(
            numero_evaluacion='EV-001',
            codigo_sinpad='   ',
            tipo_peligro_id=3,
            fecha_emergencia=date(2026, 10, 1),
            c_usuari_login='mmedina',
        )

    assert exc.value.conflict is False
    assert 'codigo_sinpad' in exc.value.message


def test_create_rejects_existing_codigo_sinpad():
    with (
        patch('app_sgbh.services.emergencia.transaction.atomic'),
        patch('app_sgbh.services.emergencia.TipoPeligro') as tipo_peligro,
        patch('app_sgbh.services.emergencia.Emergencia') as emergencia,
    ):
        tipo_peligro.objects.filter.return_value.exists.return_value = True
        emergencia.objects.filter.return_value.exists.return_value = True

        with pytest.raises(EmergenciaServiceError) as exc:
            EmergenciaService.create(
                numero_evaluacion='EV-001',
                codigo_sinpad='  sin-001  ',
                tipo_peligro_id=3,
                fecha_emergencia=date(2026, 10, 1),
                c_usuari_login='mmedina',
            )

    assert exc.value.conflict is True
    assert exc.value.message == 'Ya existe una emergencia con el código SINPAD indicado'
    emergencia.objects.filter.assert_called_once_with(codigo_sinpad__iexact='sin-001')
    emergencia.assert_not_called()


def test_create_rejects_unknown_tipo_peligro():
    with (
        patch('app_sgbh.services.emergencia.transaction.atomic'),
        patch('app_sgbh.services.emergencia.TipoPeligro') as tipo_peligro,
        patch('app_sgbh.services.emergencia.Emergencia') as emergencia,
    ):
        tipo_peligro.objects.filter.return_value.exists.return_value = False

        with pytest.raises(EmergenciaServiceError) as exc:
            EmergenciaService.create(
                numero_evaluacion='EV-001',
                codigo_sinpad='SIN-001',
                tipo_peligro_id=99,
                fecha_emergencia=date(2026, 10, 1),
                c_usuari_login='mmedina',
            )

    assert exc.value.conflict is False
    assert exc.value.message == 'El tipo de peligro indicado no existe'
    emergencia.objects.filter.assert_not_called()
    emergencia.assert_not_called()


def test_create_saves_when_codigo_sinpad_is_new():
    with (
        patch('app_sgbh.services.emergencia.transaction.atomic'),
        patch('app_sgbh.services.emergencia.TipoPeligro') as tipo_peligro,
        patch('app_sgbh.services.emergencia.Emergencia') as emergencia,
        patch('app_sgbh.services.emergencia._formularios_con_distrito', return_value='qs'),
    ):
        tipo_peligro.objects.filter.return_value.exists.return_value = True
        emergencia.objects.filter.return_value.exists.return_value = False
        emergencia.return_value.pk = 9
        stored = (
            emergencia.objects.select_related.return_value
            .prefetch_related.return_value.get.return_value
        )

        result = EmergenciaService.create(
            numero_evaluacion='EV-001',
            codigo_sinpad='SIN-001',
            tipo_peligro_id=3,
            fecha_emergencia=date(2026, 10, 1),
            c_usuari_login=' mmedina ',
            hora_ocurrencia_estimada=time(8, 30),
            esta_activo=True,
        )

    assert result is stored
    emergencia.assert_called_once_with(
        numero_evaluacion='EV-001',
        codigo_sinpad='SIN-001',
        tipo_peligro_id=3,
        fecha_emergencia=date(2026, 10, 1),
        hora_ocurrencia_estimada=time(8, 30),
        esta_activo=True,
        c_usuari_login='mmedina',
    )
    emergencia.return_value.save.assert_called_once_with()


def test_post_emergencias_returns_conflict_when_codigo_sinpad_exists():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/emergencias/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.emergencia_view.EmergenciaService.create',
        side_effect=EmergenciaServiceError(
            'Ya existe una emergencia con el código SINPAD indicado',
            conflict=True,
        ),
    ):
        response = EmergenciaListView.as_view()(request)

    assert response.status_code == 409
    assert response.data['error'] == 'Ya existe una emergencia con el código SINPAD indicado'


def test_post_emergencias_returns_created_emergency():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/emergencias/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    created = {'emergencia_id': 9, 'codigo_sinpad': 'SIN-001'}
    instance = object()

    with (
        patch(
            'app_sgbh.views.emergencia_view.EmergenciaService.create',
            return_value=instance,
        ) as create,
        patch('app_sgbh.views.emergencia_view.EmergenciaSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = created
        response = EmergenciaListView.as_view()(request)

    assert response.status_code == 201
    assert response.data == created
    create.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert create.call_args.kwargs['c_usuari_login'] == 'mmedina'
    assert create.call_args.kwargs['codigo_sinpad'] == 'SIN-001'
