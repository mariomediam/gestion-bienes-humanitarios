from django.db import transaction

from ..db_router import DB_ALIAS
from ..models import Persona
from .formulario_2a import Formulario2AService, Formulario2AServiceError
from .formulario_2a_familia import (
    Formulario2AFamiliaService,
    Formulario2AFamiliaServiceError,
)
from .formulario_2a_integrante import (
    Formulario2AIntegranteService,
    Formulario2AIntegranteServiceError,
)
from .formulario_2a_medio_vida import (
    Formulario2AMedioVidaService,
    Formulario2AMedioVidaServiceError,
)
from .formulario_2a_vivienda import (
    Formulario2AViviendaService,
    Formulario2AViviendaServiceError,
)
from .persona import PersonaService, PersonaServiceError

_USUARIO_LOGIN_MAX_LENGTH = 20
_ERRORES_SERVICIO = (
    Formulario2AServiceError,
    Formulario2AViviendaServiceError,
    Formulario2AFamiliaServiceError,
    Formulario2AIntegranteServiceError,
    Formulario2AMedioVidaServiceError,
    PersonaServiceError,
)


class Formulario2ACargaServiceError(Exception):
    """Business rule violation while loading a mobile JSON file."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class Formulario2ACargaService:
    @staticmethod
    def cargar(*, formularios, c_usuari_login):
        """Insert every Formulario 2A from one mobile JSON file.

        The whole file is one transaction. A failure leaves no rows from
        that file. Child order numbers are assigned by the existing create
        services. c_usuari_login comes from the authenticated user.
        A persona with tipo and numero de documento is reused when the
        surnames and given names match the stored row. A persona without a
        document is reused when surnames, given names and birth date match.
        Reused rows stay as stored.
        """
        login = str(c_usuari_login or '').strip()
        if login == '' or len(login) > _USUARIO_LOGIN_MAX_LENGTH:
            raise Formulario2ACargaServiceError('No se pudo identificar al usuario')

        with transaction.atomic(using=DB_ALIAS):
            creados = []
            for indice, formulario in enumerate(formularios, start=1):
                creados.append(_cargar_formulario(formulario, login, indice))
        return creados


def _cargar_formulario(formulario, login, indice):
    datos = dict(formulario)
    viviendas = datos.pop('viviendas')
    ruta = f'Formulario {indice}'
    guardado = _ejecutar(
        ruta,
        lambda: Formulario2AService.create(c_usuari_login=login, **datos),
    )
    for indice_vivienda, vivienda in enumerate(viviendas, start=1):
        _cargar_vivienda(
            vivienda,
            guardado.pk,
            f'{ruta}, vivienda {indice_vivienda}',
            login,
        )
    return _ejecutar(ruta, lambda: Formulario2AService.get(guardado.pk))


def _cargar_vivienda(vivienda, formulario_2a_id, ruta, login):
    datos = dict(vivienda)
    familias = datos.pop('familias')
    guardada = _ejecutar(
        ruta,
        lambda: Formulario2AViviendaService.create(
            formulario_2a_id=formulario_2a_id,
            **datos,
        ),
    )
    for indice, familia in enumerate(familias, start=1):
        _cargar_familia(familia, guardada.pk, f'{ruta}, familia {indice}', login)


def _cargar_familia(familia, vivienda_id, ruta, login):
    datos = dict(familia)
    integrantes = datos.pop('integrantes')
    medios_vida = datos.pop('medios_vida')
    guardada = _ejecutar(
        ruta,
        lambda: Formulario2AFamiliaService.create(vivienda_id=vivienda_id),
    )
    for indice, integrante in enumerate(integrantes, start=1):
        _cargar_integrante(
            integrante,
            guardada.pk,
            f'{ruta}, integrante {indice}',
            login,
        )
    for indice, medio_vida in enumerate(medios_vida, start=1):
        _cargar_medio_vida(
            medio_vida,
            guardada.pk,
            f'{ruta}, medio de vida {indice}',
        )


def _cargar_integrante(integrante, familia_id, ruta, login):
    datos = dict(integrante)
    persona_datos = datos.pop('persona')
    persona = _ejecutar(ruta, lambda: _reutilizar_o_crear(persona_datos, login))
    datos['familia_id'] = familia_id
    datos['persona_id'] = persona.pk
    _ejecutar(ruta, lambda: Formulario2AIntegranteService.create(**datos))


def _cargar_medio_vida(medio_vida, familia_id, ruta):
    datos = dict(medio_vida)
    datos['familia_id'] = familia_id
    _ejecutar(ruta, lambda: Formulario2AMedioVidaService.create(**datos))


def _reutilizar_o_crear(datos, login):
    """Return the stored persona, or insert one when it does not exist."""
    tipo_documento_id = datos.get('tipo_documento_id')
    numero_documento = datos.get('numero_documento')
    if tipo_documento_id is not None and numero_documento:
        coincidencias = _coincidencias(
            tipo_documento_id=tipo_documento_id,
            numero_documento__iexact=numero_documento,
        )
        if len(coincidencias) > 1:
            raise Formulario2ACargaServiceError(
                'Existe más de una persona con el tipo y número de documento indicados',
                conflict=True,
            )
        if len(coincidencias) == 1:
            _exigir_mismo_nombre(coincidencias[0], datos)
            return coincidencias[0]
    else:
        coincidencias = _coincidencias(
            apellido_paterno__iexact=datos['apellido_paterno'],
            apellido_materno__iexact=datos['apellido_materno'],
            nombres__iexact=datos['nombres'],
            fecha_nacimiento=datos.get('fecha_nacimiento'),
        )
        if len(coincidencias) > 1:
            raise Formulario2ACargaServiceError(
                'Existe más de una persona con los mismos apellidos, nombres y fecha de nacimiento',
                conflict=True,
            )
        if len(coincidencias) == 1:
            return coincidencias[0]

    return PersonaService.create(c_usuari_login=login, **datos)


def _coincidencias(**filtros):
    return list(Persona.objects.filter(**filtros).order_by('persona_id')[:2])


def _exigir_mismo_nombre(persona, datos):
    if _mismo_nombre(persona, datos):
        return
    raise Formulario2ACargaServiceError(
        'El nombre de la persona '
        f'{_nombre_completo(datos)} no coincide con lo registrado '
        f'en la base de datos ({_nombre_completo(persona)})'
    )


def _mismo_nombre(persona, datos):
    return (
        _texto(persona.apellido_paterno) == _texto(datos['apellido_paterno'])
        and _texto(persona.apellido_materno) == _texto(datos['apellido_materno'])
        and _texto(persona.nombres) == _texto(datos['nombres'])
    )


def _nombre_completo(origen):
    if isinstance(origen, dict):
        apellido_paterno = origen['apellido_paterno']
        apellido_materno = origen['apellido_materno']
        nombres = origen['nombres']
    else:
        apellido_paterno = origen.apellido_paterno
        apellido_materno = origen.apellido_materno
        nombres = origen.nombres
    return (
        f'{str(apellido_paterno).strip()} '
        f'{str(apellido_materno).strip()} '
        f'{str(nombres).strip()}'
    )


def _texto(value):
    return str(value or '').strip().casefold()


def _ejecutar(ruta, funcion):
    try:
        return funcion()
    except Formulario2ACargaServiceError as exc:
        raise Formulario2ACargaServiceError(
            f'{ruta}: {exc.message}',
            conflict=exc.conflict,
            not_found=exc.not_found,
        ) from exc
    except _ERRORES_SERVICIO as exc:
        raise Formulario2ACargaServiceError(
            f'{ruta}: {exc.message}',
            conflict=exc.conflict,
            not_found=exc.not_found,
        ) from exc
