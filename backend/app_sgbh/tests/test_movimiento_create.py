from contextlib import ExitStack, contextmanager
from datetime import date, datetime, timezone as dt_timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.db import IntegrityError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.movimiento import MovimientoService, MovimientoServiceError
from app_sgbh.views.movimiento_view import MovimientoCreateView

FIXED_NOW = datetime(2026, 10, 16, 18, 59, tzinfo=dt_timezone.utc)


@contextmanager
def _patched(*, tipo=None, bienes=None, origen=None, stored=None):
    with ExitStack() as stack:
        mocks = {
            'atomic': stack.enter_context(
                patch('app_sgbh.services.movimiento.transaction.atomic')
            ),
            'now': stack.enter_context(
                patch(
                    'app_sgbh.services.movimiento.timezone.now',
                    return_value=FIXED_NOW,
                )
            ),
            'almacen': stack.enter_context(
                patch('app_sgbh.services.movimiento.Almacen')
            ),
            'tipo': stack.enter_context(
                patch('app_sgbh.services.movimiento.TipoMovimiento')
            ),
            'estado': stack.enter_context(
                patch('app_sgbh.services.movimiento.EstadoMovimiento')
            ),
            'personal': stack.enter_context(
                patch('app_sgbh.services.movimiento.Personal')
            ),
            'bien': stack.enter_context(patch('app_sgbh.services.movimiento.Bien')),
            'movimiento': stack.enter_context(
                patch('app_sgbh.services.movimiento.Movimiento')
            ),
            'detalle': stack.enter_context(
                patch('app_sgbh.services.movimiento.MovimientoDetalle')
            ),
        }
        tipo_row = tipo or SimpleNamespace(
            naturaleza='E',
            requiere_movimiento_origen=False,
            esta_activo=True,
        )
        mocks['almacen'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=True)
        )
        mocks['tipo'].objects.filter.return_value.first.return_value = tipo_row
        mocks['estado'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=True)
        )
        mocks['personal'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=True, es_encargado_almacen=True)
        )
        if bienes is None:
            bienes = [SimpleNamespace(bien_id=8, esta_activo=True)]
        mocks['bien'].objects.filter.return_value = bienes
        mocks['movimiento'].objects.filter.return_value.first.return_value = origen
        mocks['movimiento'].return_value.pk = 15
        mocks['detalle'].objects.order_by.return_value = Mock(spec=[])
        if stored is None:
            stored = SimpleNamespace(movimiento_id=15, detalles=[])
        mocks['movimiento'].objects.prefetch_related.return_value.get.return_value = (
            stored
        )
        yield mocks


def _line(**overrides):
    data = {
        'bien_id': 8,
        'cantidad': Decimal('3.000000'),
        'cantidad_texto': '3',
        'es_devolvible': False,
        'observacion': 'Caja',
    }
    data.update(overrides)
    return data


def _payload(**overrides):
    data = {
        'almacen_id': 1,
        'tipo_movimiento_id': 2,
        'estado_movimiento_id': 1,
        'movimiento_origen_id': None,
        'fecha_movimiento': datetime(2026, 10, 16, 9, 30),
        'documento_referencia': 'FAC-1',
        'fecha_documento': date(2026, 10, 15),
        'destinatario': 'Municipalidad',
        'observacion': 'Ingreso',
        'fecha_confirmacion': None,
        'encargado_almacen_id': 4,
        'c_usuari_login': 'mmedina',
        'detalles': [_line()],
    }
    data.update(overrides)
    return data


def _tipo(**overrides):
    data = {
        'naturaleza': 'E',
        'requiere_movimiento_origen': False,
        'esta_activo': True,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_create_inserts_header_and_detail_in_one_transaction():
    stored = SimpleNamespace(movimiento_id=15, detalles=[])
    with _patched(stored=stored) as mocks:
        result = MovimientoService.create(
            **_payload(
                documento_referencia='  FAC-1  ',
                c_usuari_login=' mmedina ',
                detalles=[_line(cantidad_texto='   ', observacion='  ')],
            )
        )

    assert result is stored
    mocks['atomic'].assert_called_once_with(using='sgbh')
    mocks['movimiento'].assert_called_once_with(
        almacen_id=1,
        tipo_movimiento_id=2,
        estado_movimiento_id=1,
        movimiento_origen_id=None,
        fecha_movimiento=datetime(2026, 10, 16, 9, 30),
        documento_referencia='FAC-1',
        fecha_documento=date(2026, 10, 15),
        destinatario='Municipalidad',
        observacion='Ingreso',
        fecha_confirmacion=None,
        encargado_almacen_id=4,
        c_usuari_login='mmedina',
        fecha_creacion=FIXED_NOW,
        fecha_modificacion=None,
    )
    mocks['movimiento'].return_value.save.assert_called_once_with()
    mocks['detalle'].assert_called_once_with(
        movimiento_id=15,
        bien_id=8,
        cantidad=Decimal('3.000000'),
        cantidad_texto=None,
        es_devolvible=False,
        observacion=None,
        fecha_creacion=FIXED_NOW,
    )
    mocks['detalle'].return_value.save.assert_called_once_with()
    mocks['movimiento'].objects.filter.assert_not_called()


def test_create_allows_negative_devolvible_lines_for_salida():
    with _patched(
        tipo=_tipo(naturaleza='S'),
        bienes=[SimpleNamespace(bien_id=8, esta_activo=True)],
    ) as mocks:
        MovimientoService.create(
            **_payload(
                detalles=[
                    _line(cantidad=Decimal('-5'), es_devolvible=False),
                    _line(cantidad=Decimal('-2'), es_devolvible=True),
                ]
            )
        )

    assert mocks['detalle'].call_count == 2
    assert mocks['detalle'].call_args_list[0].kwargs['es_devolvible'] is False
    assert mocks['detalle'].call_args_list[1].kwargs['es_devolvible'] is True
    mocks['bien'].objects.filter.assert_called_once_with(bien_id__in=[8, 8])


def test_create_allows_both_signs_for_naturaleza_mixta():
    with _patched(
        tipo=_tipo(naturaleza='M'),
        bienes=[
            SimpleNamespace(bien_id=8, esta_activo=True),
            SimpleNamespace(bien_id=9, esta_activo=True),
        ],
    ) as mocks:
        MovimientoService.create(
            **_payload(
                detalles=[
                    _line(bien_id=8, cantidad=Decimal('2'), es_devolvible=False),
                    _line(
                        bien_id=9,
                        cantidad=Decimal('-1'),
                        es_devolvible=True,
                    ),
                ]
            )
        )

    assert [call.kwargs['cantidad'] for call in mocks['detalle'].call_args_list] == [
        Decimal('2'),
        Decimal('-1'),
    ]


def test_create_stores_origen_when_the_type_requires_it():
    with _patched(
        tipo=_tipo(requiere_movimiento_origen=True),
        origen=SimpleNamespace(movimiento_id=20),
    ) as mocks:
        MovimientoService.create(**_payload(movimiento_origen_id=20))

    assert mocks['movimiento'].call_args.kwargs['movimiento_origen_id'] == 20
    mocks['movimiento'].objects.filter.assert_called_once_with(pk=20)


def test_create_stores_optional_origen_when_the_type_does_not_require_it():
    with _patched(origen=SimpleNamespace(movimiento_id=20)) as mocks:
        MovimientoService.create(**_payload(movimiento_origen_id=20))

    assert mocks['movimiento'].call_args.kwargs['movimiento_origen_id'] == 20


@pytest.mark.parametrize(
    ('changes', 'tipo', 'bienes', 'origen', 'message', 'conflict'),
    [
        (
            {'detalles': [_line(cantidad=Decimal('-1'))]},
            None,
            None,
            None,
            'La cantidad debe ser positiva para un tipo de movimiento de entrada',
            False,
        ),
        (
            {'detalles': [_line(cantidad=Decimal('1'), es_devolvible=False)]},
            _tipo(naturaleza='S'),
            None,
            None,
            'La cantidad debe ser negativa para un tipo de movimiento de salida',
            False,
        ),
        (
            {'detalles': [_line(cantidad=Decimal('0'))]},
            None,
            None,
            None,
            'El campo cantidad debe ser distinto de cero',
            False,
        ),
        (
            {'detalles': [_line(es_devolvible=True)]},
            None,
            None,
            None,
            'Un detalle con cantidad positiva no puede ser devolvible',
            False,
        ),
        (
            {
                'detalles': [
                    _line(cantidad=Decimal('-1'), es_devolvible=True),
                    _line(cantidad=Decimal('-2'), es_devolvible=True),
                ]
            },
            _tipo(naturaleza='S'),
            [SimpleNamespace(bien_id=8, esta_activo=True)],
            None,
            'El bien ya está registrado con la misma modalidad de devolución en este movimiento',
            True,
        ),
        (
            {'movimiento_origen_id': None},
            _tipo(requiere_movimiento_origen=True),
            None,
            None,
            'El tipo de movimiento requiere un movimiento de origen',
            False,
        ),
        (
            {'movimiento_origen_id': 20},
            _tipo(requiere_movimiento_origen=True),
            None,
            None,
            'El movimiento de origen indicado no existe',
            False,
        ),
        (
            {},
            _tipo(naturaleza='X'),
            None,
            None,
            'La naturaleza del tipo de movimiento no es válida',
            False,
        ),
        (
            {'c_usuari_login': '   '},
            None,
            None,
            None,
            'El campo c_usuari_login es obligatorio',
            False,
        ),
        (
            {'c_usuari_login': 'x' * 21},
            None,
            None,
            None,
            'El campo c_usuari_login no debe superar 20 caracteres',
            False,
        ),
        (
            {'detalles': []},
            None,
            None,
            None,
            'Debe registrar al menos un detalle',
            False,
        ),
    ],
)
def test_create_rejects_invalid_movement(changes, tipo, bienes, origen, message, conflict):
    with _patched(tipo=tipo, bienes=bienes, origen=origen) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload(**changes))

    assert exc.value.message == message
    assert exc.value.conflict is conflict
    mocks['movimiento'].assert_not_called()


def test_create_rejects_missing_almacen_before_insert():
    with _patched() as mocks:
        mocks['almacen'].objects.filter.return_value.first.return_value = None
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El almacén indicado no existe'
    mocks['tipo'].objects.filter.assert_not_called()
    mocks['movimiento'].assert_not_called()


def test_create_rejects_inactive_almacen():
    with _patched() as mocks:
        mocks['almacen'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=False)
        )
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El almacén indicado no está activo'
    mocks['movimiento'].assert_not_called()


def test_create_rejects_inactive_tipo():
    with _patched(tipo=_tipo(esta_activo=False)) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El tipo de movimiento indicado no está activo'
    mocks['movimiento'].assert_not_called()


def test_create_rejects_inactive_estado():
    with _patched() as mocks:
        mocks['estado'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=False)
        )
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El estado de movimiento indicado no está activo'
    mocks['movimiento'].assert_not_called()


def test_create_rejects_missing_bien():
    with _patched(bienes=[]) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El bien indicado no existe'
    mocks['movimiento'].assert_not_called()


def test_create_rejects_inactive_bien():
    with _patched(
        bienes=[SimpleNamespace(bien_id=8, esta_activo=False)]
    ) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El bien indicado no está activo'
    mocks['movimiento'].assert_not_called()


def test_create_rejects_inactive_encargado():
    with _patched() as mocks:
        mocks['personal'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=False, es_encargado_almacen=True)
        )
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El encargado de almacén indicado no está activo'
    mocks['bien'].objects.filter.assert_not_called()
    mocks['movimiento'].assert_not_called()


def test_create_rejects_personal_that_is_not_encargado():
    with _patched() as mocks:
        mocks['personal'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=True, es_encargado_almacen=False)
        )
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.message == 'El personal indicado no es encargado de almacén'
    mocks['movimiento'].assert_not_called()


def test_create_maps_detail_integrity_error_to_conflict():
    with _patched() as mocks:
        mocks['detalle'].return_value.save.side_effect = IntegrityError()
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.create(**_payload())

    assert exc.value.conflict is True
    assert 'misma modalidad' in exc.value.message
    mocks['movimiento'].objects.prefetch_related.assert_not_called()


def _stored_movimiento():
    creado = FIXED_NOW
    return SimpleNamespace(
        movimiento_id=15,
        almacen_id=1,
        tipo_movimiento_id=2,
        estado_movimiento_id=1,
        movimiento_origen_id=None,
        fecha_movimiento=datetime(2026, 10, 16, 9, 30, tzinfo=dt_timezone.utc),
        documento_referencia='FAC-1',
        fecha_documento=date(2026, 10, 15),
        destinatario='Municipalidad',
        observacion='Ingreso',
        fecha_confirmacion=None,
        encargado_almacen_id=4,
        c_usuari_login='mmedina',
        fecha_creacion=creado,
        fecha_modificacion=None,
        detalles=[
            SimpleNamespace(
                movimiento_detalle_id=100,
                movimiento_id=15,
                bien_id=8,
                cantidad=Decimal('3.000000'),
                cantidad_texto='3',
                es_devolvible=False,
                observacion='Caja',
                fecha_creacion=creado,
            )
        ],
    )


def _authenticate(request):
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))


def _body(**overrides):
    data = {
        'almacen_id': 1,
        'tipo_movimiento_id': 2,
        'estado_movimiento_id': 1,
        'fecha_movimiento': '2026-10-16T09:30:00',
        'documento_referencia': '  FAC-1  ',
        'fecha_documento': '2026-10-15',
        'destinatario': ' Municipalidad ',
        'observacion': ' Ingreso ',
        'encargado_almacen_id': 4,
        'c_usuari_login': ' mmedina ',
        'detalles': [
            {
                'bien_id': 8,
                'cantidad': '3',
                'cantidad_texto': ' 3 ',
                'es_devolvible': False,
                'observacion': ' Caja ',
            }
        ],
    }
    data.update(overrides)
    return data


def test_post_movimientos_returns_created_movement():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/movimientos/', _body(), format='json')
    _authenticate(request)
    created = _stored_movimiento()

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.create',
        return_value=created,
    ) as create:
        response = MovimientoCreateView.as_view()(request)

    assert response.status_code == 201
    kwargs = create.call_args.kwargs
    assert kwargs['almacen_id'] == 1
    assert kwargs['tipo_movimiento_id'] == 2
    assert kwargs['estado_movimiento_id'] == 1
    assert kwargs['movimiento_origen_id'] is None
    assert kwargs['fecha_confirmacion'] is None
    assert kwargs['documento_referencia'] == 'FAC-1'
    assert kwargs['fecha_documento'] == date(2026, 10, 15)
    assert kwargs['destinatario'] == 'Municipalidad'
    assert kwargs['c_usuari_login'] == 'mmedina'
    assert kwargs['detalles'][0]['bien_id'] == 8
    assert kwargs['detalles'][0]['cantidad'] == Decimal('3.000000')
    assert kwargs['detalles'][0]['cantidad_texto'] == '3'
    assert kwargs['detalles'][0]['es_devolvible'] is False
    fecha = kwargs['fecha_movimiento']
    assert (fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute) == (
        2026,
        10,
        16,
        9,
        30,
    )
    assert response.data['movimiento_id'] == 15
    assert response.data['fecha_modificacion'] is None
    assert response.data['detalles'][0]['movimiento_detalle_id'] == 100
    assert response.data['detalles'][0]['bien_id'] == 8


def test_post_movimientos_returns_conflict_for_duplicate_detail():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/movimientos/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.create',
        side_effect=MovimientoServiceError(
            'El bien ya está registrado con la misma modalidad de devolución en este movimiento',
            conflict=True,
        ),
    ):
        response = MovimientoCreateView.as_view()(request)

    assert response.status_code == 409
    assert 'misma modalidad' in response.data['error']


def test_post_movimientos_returns_service_error():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/movimientos/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.create',
        side_effect=MovimientoServiceError('El almacén indicado no está activo'),
    ):
        response = MovimientoCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El almacén indicado no está activo'


def test_post_movimientos_hides_unexpected_errors():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/movimientos/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.create',
        side_effect=RuntimeError('sql'),
    ):
        response = MovimientoCreateView.as_view()(request)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo registrar el movimiento de almacén'


@pytest.mark.parametrize(
    ('body', 'message'),
    [
        ({}, 'El campo almacen_id es obligatorio'),
        (
            _body(detalles=[]),
            'Debe registrar al menos un detalle',
        ),
        (
            _body(detalles=[{}]),
            'El campo bien_id es obligatorio',
        ),
        (
            _body(detalles=['pala']),
            'Cada detalle debe ser un objeto',
        ),
        (
            _body(fecha_movimiento='16/10/2026'),
            'El campo fecha_movimiento debe tener el formato AAAA-MM-DD HH:MM:SS',
        ),
        (
            _body(c_usuari_login='   '),
            'El campo c_usuari_login es obligatorio',
        ),
        ([], 'El cuerpo de la solicitud no es válido'),
    ],
)
def test_post_movimientos_rejects_invalid_body(body, message):
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/movimientos/', body, format='json')
    _authenticate(request)

    with patch('app_sgbh.views.movimiento_view.MovimientoService.create') as create:
        response = MovimientoCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == message
    create.assert_not_called()
