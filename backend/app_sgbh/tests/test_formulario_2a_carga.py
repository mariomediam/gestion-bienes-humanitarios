import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers.formulario_2a_carga import (
    CargaFormularios2ASerializer,
    mensaje_error_carga,
)
from app_sgbh.services.formulario_2a import Formulario2AServiceError
from app_sgbh.services.formulario_2a_carga import (
    Formulario2ACargaService,
    Formulario2ACargaServiceError,
)
from app_sgbh.views.formulario_2a_carga_view import Formulario2ACargaView

_EJEMPLO = (
    Path(__file__).resolve().parents[2] / 'ejemplos' / 'carga-formularios-2a.json'
)


def _persona(**overrides):
    data = {
        'tipo_documento_id': 1,
        'numero_documento': '45678901',
        'apellido_paterno': 'Garcia',
        'apellido_materno': 'Ramos',
        'nombres': 'Ana',
        'fecha_nacimiento': '1988-04-12',
        'sexo': 'F',
        'telefono': '',
        'correo': '',
        'esta_activo': True,
    }
    data.update(overrides)
    return data


def _integrante(**persona_overrides):
    return {
        'persona': _persona(**persona_overrides),
        'rol_familiar_id': 1,
        'edad': 38,
        'condicion_persona_id': 1,
    }


def _formulario(**overrides):
    data = {
        'emergencia_id': 1,
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'fecha_empadronamiento': '2026-10-15',
        'evaluador_id': 1,
        'estado_registro_id': 1,
        'viviendas': [
            {
                'numero_lote': '04',
                'tipo_uso_instalacion_id': 1,
                'familias': [
                    {
                        'integrantes': [_integrante()],
                        'medios_vida': [
                            {'tipo_medio_vida_id': 1, 'cantidad': 4},
                        ],
                    }
                ],
            }
        ],
    }
    data.update(overrides)
    return data


def _parse(data):
    serializer = CargaFormularios2ASerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, mensaje_error_carga(serializer.errors)


def _consulta(personas):
    resultado = MagicMock()
    resultado.__iter__.return_value = iter(personas)
    consulta = MagicMock()
    consulta.order_by.return_value.__getitem__.return_value = resultado
    return consulta


def _persona_guardada(**overrides):
    data = {
        'pk': 9,
        'apellido_paterno': 'Garcia',
        'apellido_materno': 'Ramos',
        'nombres': 'Ana',
    }
    data.update(overrides)
    return SimpleNamespace(**data)


class _Carga:
    def __init__(self, personas_por_llamada):
        self.personas_por_llamada = list(personas_por_llamada)
        self.formulario = MagicMock()
        self.vivienda = MagicMock()
        self.familia = MagicMock()
        self.integrante = MagicMock()
        self.medio_vida = MagicMock()
        self.persona = MagicMock()
        self.objects = MagicMock()
        creado = SimpleNamespace(pk=10)
        self.formulario.create.return_value = creado
        self.formulario.get.return_value = creado
        self.vivienda.create.return_value = SimpleNamespace(pk=20)
        self.familia.create.return_value = SimpleNamespace(pk=30)
        self.persona.create.return_value = _persona_guardada(pk=7)
        self.objects.filter.side_effect = self._filter

    def _filter(self, **_filtros):
        if self.personas_por_llamada:
            personas = self.personas_por_llamada.pop(0)
        else:
            personas = []
        return _consulta(personas)

    def __enter__(self):
        self._parche = patch.multiple(
            'app_sgbh.services.formulario_2a_carga',
            transaction=MagicMock(),
            Formulario2AService=self.formulario,
            Formulario2AViviendaService=self.vivienda,
            Formulario2AFamiliaService=self.familia,
            Formulario2AIntegranteService=self.integrante,
            Formulario2AMedioVidaService=self.medio_vida,
            PersonaService=self.persona,
            Persona=MagicMock(objects=self.objects),
        )
        self._parche.start()
        self._parche_atomic = patch(
            'app_sgbh.services.formulario_2a_carga.transaction.atomic'
        )
        self._parche_atomic.start()
        return self

    def __exit__(self, *args):
        self._parche_atomic.stop()
        self._parche.stop()


def test_ejemplo_json_no_trae_los_datos_que_completa_la_pantalla():
    ejemplo = json.loads(_EJEMPLO.read_text(encoding='utf-8'))
    formulario = ejemplo['formularios'][0]

    for campo in (
        'emergencia_id',
        'departamento_id',
        'provincia_id',
        'distrito_id',
        'institucion',
        'evaluador_id',
        'estado_registro_id',
    ):
        assert campo not in formulario
    assert 'rol_familiar_id' not in (
        formulario['viviendas'][0]['familias'][0]['integrantes'][0]
    )


def test_ejemplo_json_es_valido_despues_de_completar_la_pantalla():
    ejemplo = json.loads(_EJEMPLO.read_text(encoding='utf-8'))
    for formulario in ejemplo['formularios']:
        formulario.update({
            'emergencia_id': 4,
            'departamento_id': '20',
            'provincia_id': '01',
            'distrito_id': '01',
            'institucion': 'Municipalidad Provincial de Piura',
            'evaluador_id': 7,
            'estado_registro_id': 1,
        })
        for vivienda in formulario['viviendas']:
            for familia in vivienda['familias']:
                for indice, integrante in enumerate(familia['integrantes']):
                    integrante['rol_familiar_id'] = 1 if indice == 0 else 2

    parsed, error = _parse(ejemplo)

    assert error is None
    assert len(parsed['formularios']) == 2
    assert parsed['formularios'][0]['fecha_empadronamiento'] == date(2026, 10, 15)
    assert parsed['formularios'][0]['institucion'] == 'Municipalidad Provincial de Piura'
    assert parsed['formularios'][0]['estado_registro_id'] == 1
    roles = [
        integrante['rol_familiar_id']
        for integrante in parsed['formularios'][0]['viviendas'][0]['familias'][0]['integrantes']
    ]
    assert roles == [1, 2]
    persona = parsed['formularios'][0]['viviendas'][0]['familias'][0]['integrantes'][1]
    assert persona['persona']['tipo_documento_id'] is None
    assert persona['persona']['numero_documento'] is None


def test_parse_permite_formulario_sin_viviendas():
    parsed, error = _parse({
        'formularios': [
            {
                'emergencia_id': 1,
                'departamento_id': '20',
                'provincia_id': '01',
                'distrito_id': '01',
                'fecha_empadronamiento': '2026-10-15',
                'evaluador_id': 1,
                'estado_registro_id': 1,
            }
        ]
    })

    assert error is None
    assert parsed['formularios'][0]['viviendas'] == []
    assert parsed['formularios'][0]['numero_hoja'] == 1


def test_parse_rechaza_archivo_vacio():
    _parsed, error = _parse({'formularios': []})

    assert error == 'El archivo no contiene formularios'


def test_parse_indica_la_posicion_del_error():
    payload = _formulario()
    payload['viviendas'][0]['familias'][0]['integrantes'][0]['persona'].pop('nombres')
    _parsed, error = _parse({'formularios': [payload, _formulario()]})

    assert error == (
        'Formulario 1, vivienda 1, familia 1, integrante 1, persona: '
        'El campo nombres es obligatorio'
    )


def test_cargar_reutiliza_persona_cuando_el_nombre_coincide():
    existente = _persona_guardada(apellido_paterno='GARCIA', nombres='ana')
    with _Carga([[existente]]) as carga:
        creados = Formulario2ACargaService.cargar(
            formularios=_parse({'formularios': [_formulario()]})[0]['formularios'],
            c_usuari_login='mmedina',
        )

    assert creados[0].pk == 10
    carga.persona.create.assert_not_called()
    carga.integrante.create.assert_called_once()
    assert carga.integrante.create.call_args.kwargs['persona_id'] == 9
    assert carga.formulario.create.call_args.kwargs['c_usuari_login'] == 'mmedina'


def test_cargar_cancela_cuando_el_nombre_no_coincide():
    existente = _persona_guardada(nombres='Luis')
    with _Carga([[existente]]) as carga:
        with pytest.raises(Formulario2ACargaServiceError) as exc:
            Formulario2ACargaService.cargar(
                formularios=_parse({'formularios': [_formulario()]})[0]['formularios'],
                c_usuari_login='mmedina',
            )

    assert exc.value.message == (
        'Formulario 1, vivienda 1, familia 1, integrante 1: '
        'El nombre de la persona Garcia Ramos Ana no coincide con lo registrado '
        'en la base de datos (Garcia Ramos Luis)'
    )
    assert exc.value.conflict is False
    carga.persona.create.assert_not_called()
    carga.integrante.create.assert_not_called()


def test_cargar_crea_persona_cuando_el_documento_no_existe():
    with _Carga([[]]) as carga:
        Formulario2ACargaService.cargar(
            formularios=_parse({'formularios': [_formulario()]})[0]['formularios'],
            c_usuari_login='mmedina',
        )

    carga.persona.create.assert_called_once()
    assert carga.persona.create.call_args.kwargs['c_usuari_login'] == 'mmedina'
    assert carga.persona.create.call_args.kwargs['numero_documento'] == '45678901'
    assert carga.integrante.create.call_args.kwargs['persona_id'] == 7


def test_cargar_reutiliza_persona_sin_documento_por_identidad():
    existente = _persona_guardada(pk=4)
    formulario = _formulario()
    formulario['viviendas'][0]['familias'][0]['integrantes'][0] = _integrante(
        tipo_documento_id=None,
        numero_documento=None,
        fecha_nacimiento='2016-09-03',
    )
    with _Carga([[existente]]) as carga:
        Formulario2ACargaService.cargar(
            formularios=_parse({'formularios': [formulario]})[0]['formularios'],
            c_usuari_login='mmedina',
        )

    carga.persona.create.assert_not_called()
    assert carga.integrante.create.call_args.kwargs['persona_id'] == 4
    filtro = carga.objects.filter.call_args.kwargs
    assert filtro['apellido_paterno__iexact'] == 'Garcia'
    assert filtro['fecha_nacimiento'] == date(2016, 9, 3)


def test_cargar_crea_persona_sin_documento_cuando_la_identidad_no_existe():
    formulario = _formulario()
    formulario['viviendas'][0]['familias'][0]['integrantes'][0] = _integrante(
        tipo_documento_id=None,
        numero_documento=None,
    )
    with _Carga([[]]) as carga:
        Formulario2ACargaService.cargar(
            formularios=_parse({'formularios': [formulario]})[0]['formularios'],
            c_usuari_login='mmedina',
        )

    carga.persona.create.assert_called_once()
    assert carga.persona.create.call_args.kwargs['tipo_documento_id'] is None
    assert carga.persona.create.call_args.kwargs['numero_documento'] is None


def test_cargar_cancela_cuando_el_documento_esta_repetido():
    with _Carga([[_persona_guardada(pk=1), _persona_guardada(pk=2)]]) as carga:
        with pytest.raises(Formulario2ACargaServiceError) as exc:
            Formulario2ACargaService.cargar(
                formularios=_parse({'formularios': [_formulario()]})[0]['formularios'],
                c_usuari_login='mmedina',
            )

    assert exc.value.conflict is True
    assert 'más de una persona con el tipo y número de documento' in exc.value.message
    carga.integrante.create.assert_not_called()


def test_cargar_cancela_el_archivo_completo_si_un_formulario_falla():
    with _Carga([]) as carga:
        carga.formulario.create.side_effect = [
            SimpleNamespace(pk=10),
            Formulario2AServiceError('La emergencia indicada no existe'),
        ]
        with pytest.raises(Formulario2ACargaServiceError) as exc:
            Formulario2ACargaService.cargar(
                formularios=_parse({
                    'formularios': [
                        {
                            'emergencia_id': 1,
                            'departamento_id': '20',
                            'provincia_id': '01',
                            'distrito_id': '01',
                            'fecha_empadronamiento': '2026-10-15',
                            'evaluador_id': 1,
                            'estado_registro_id': 1,
                            'viviendas': [],
                        },
                        _formulario(emergencia_id=99, viviendas=[]),
                    ]
                })[0]['formularios'],
                c_usuari_login='mmedina',
            )

    assert exc.value.message == 'Formulario 2: La emergencia indicada no existe'
    assert carga.formulario.create.call_count == 2
    carga.vivienda.create.assert_not_called()


def test_cargar_rechaza_usuario_no_identificado():
    with pytest.raises(Formulario2ACargaServiceError) as exc:
        Formulario2ACargaService.cargar(
            formularios=_parse({'formularios': [_formulario()]})[0]['formularios'],
            c_usuari_login=' ',
        )

    assert exc.value.message == 'No se pudo identificar al usuario'


def _post(data=None, archivo=None, login='mmedina'):
    factory = APIRequestFactory()
    if archivo is not None:
        request = factory.post(
            '/api/sgbh/formularios-2a/cargar/',
            {'archivo': archivo},
            format='multipart',
        )
    else:
        request = factory.post(
            '/api/sgbh/formularios-2a/cargar/',
            data,
            format='json',
        )
    force_authenticate(request, user=ExternalUser(login=login, nombre='Mario'))
    return Formulario2ACargaView.as_view()(request)


def test_post_carga_archivo_json():
    archivo = SimpleUploadedFile(
        'carga.json',
        json.dumps({'formularios': [_formulario()]}).encode('utf-8'),
        content_type='application/json',
    )
    with (
        patch(
            'app_sgbh.views.formulario_2a_carga_view.Formulario2ACargaService.cargar',
            return_value=[SimpleNamespace(pk=10)],
        ) as cargar,
        patch(
            'app_sgbh.views.formulario_2a_carga_view.CargaFormularios2AResultadoSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = {'formularios': [{'formulario_2a_id': 10}]}
        response = _post(archivo=archivo)

    assert response.status_code == 201
    assert response.data['formularios'][0]['formulario_2a_id'] == 10
    assert cargar.call_args.kwargs['c_usuari_login'] == 'mmedina'


def test_post_carga_rechaza_extension_distinta():
    archivo = SimpleUploadedFile('carga.txt', b'{}', content_type='text/plain')
    response = _post(archivo=archivo)

    assert response.status_code == 400
    assert response.data['error'] == 'El archivo debe tener extensión .json'


def test_post_carga_rechaza_json_invalido():
    archivo = SimpleUploadedFile(
        'carga.json',
        b'{',
        content_type='application/json',
    )
    response = _post(archivo=archivo)

    assert response.status_code == 400
    assert response.data['error'] == 'El archivo no contiene un JSON válido'


def test_post_carga_acepta_el_cuerpo_json():
    with (
        patch(
            'app_sgbh.views.formulario_2a_carga_view.Formulario2ACargaService.cargar',
            return_value=[SimpleNamespace(pk=10)],
        ),
        patch(
            'app_sgbh.views.formulario_2a_carga_view.CargaFormularios2AResultadoSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = {'formularios': [{'formulario_2a_id': 10}]}
        response = _post(data={'formularios': [_formulario()]})

    assert response.status_code == 201


def test_post_carga_devuelve_el_error_de_negocio():
    with patch(
        'app_sgbh.views.formulario_2a_carga_view.Formulario2ACargaService.cargar',
        side_effect=Formulario2ACargaServiceError(
            'Formulario 1: La emergencia indicada no existe',
            not_found=True,
        ),
    ):
        response = _post(data={'formularios': [_formulario()]})

    assert response.status_code == 404
    assert response.data['error'] == 'Formulario 1: La emergencia indicada no existe'
