from rest_framework import serializers

from .formulario_2a import Formulario2ABusquedaSerializer, Formulario2ACreateSerializer
from .formulario_2a_integrante import IntegranteCreateSerializer
from .formulario_2a_medio_vida import MedioVidaCreateSerializer
from .formulario_2a_vivienda import ViviendaCreateSerializer
from .persona import PersonaCreateSerializer

_LISTAS = {
    'formularios': 'Formulario',
    'viviendas': 'vivienda',
    'familias': 'familia',
    'integrantes': 'integrante',
    'medios_vida': 'medio de vida',
}


class CargaMedioVidaSerializer(MedioVidaCreateSerializer):
    """Medio de vida inside a familia of the mobile JSON file.

    familia_id does not travel in the file. The load assigns it after the
    familia row exists.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('familia_id', None)


class CargaIntegranteSerializer(IntegranteCreateSerializer):
    """Integrante inside a familia of the mobile JSON file.

    familia_id and persona_id do not travel in the file. The persona block
    carries the same fields as the persona create endpoint.
    """

    persona = PersonaCreateSerializer(
        error_messages={
            'required': 'El campo persona es obligatorio',
            'null': 'El campo persona es obligatorio',
            'invalid': 'El campo persona no es válido',
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('familia_id', None)
        self.fields.pop('persona_id', None)


class CargaFamiliaSerializer(serializers.Serializer):
    """Familia inside a vivienda of the mobile JSON file.

    The familia row only stores vivienda_id and numero_orden. Both are
    assigned during the load.
    """

    integrantes = CargaIntegranteSerializer(many=True, required=False, default=list)
    medios_vida = CargaMedioVidaSerializer(many=True, required=False, default=list)


class CargaViviendaSerializer(ViviendaCreateSerializer):
    """Vivienda inside a formulario of the mobile JSON file.

    formulario_2a_id and numero_orden do not travel in the file.
    """

    familias = CargaFamiliaSerializer(many=True, required=False, default=list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('formulario_2a_id', None)


class CargaFormularioSerializer(Formulario2ACreateSerializer):
    """One Formulario 2A inside the mobile JSON file.

    c_usuari_login comes from the authenticated user. numero_orden of the
    child rows is assigned by the existing create services.
    """

    viviendas = CargaViviendaSerializer(many=True, required=False, default=list)


class CargaFormularios2ASerializer(serializers.Serializer):
    """JSON file produced by the mobile app.

    formularios holds every Formulario 2A to insert in one load.
    """

    formularios = CargaFormularioSerializer(
        many=True,
        allow_empty=False,
        error_messages={
            'required': 'El campo formularios es obligatorio',
            'null': 'El campo formularios es obligatorio',
            'not_a_list': 'El campo formularios debe ser una lista',
            'empty': 'El archivo no contiene formularios',
        },
    )


class CargaFormularios2AResultadoSerializer(serializers.Serializer):
    """Formularios created by one successful load."""

    formularios = Formulario2ABusquedaSerializer(many=True)


def mensaje_error_carga(errors, ruta=''):
    """Return the first nested serializer error with its position in the file."""
    if isinstance(errors, dict):
        for key, value in errors.items():
            if key == 'persona':
                siguiente = f'{ruta}, persona' if ruta else 'persona'
                found = mensaje_error_carga(value, siguiente)
            elif key in _LISTAS:
                found = _mensaje_lista(value, ruta, _LISTAS[key])
            else:
                found = mensaje_error_carga(value, ruta)
            if found:
                return found
        return 'Los datos enviados no son válidos'

    if isinstance(errors, (list, tuple)):
        if not errors:
            return 'Los datos enviados no son válidos'
        if not isinstance(errors[0], (dict, list)):
            texto = str(errors[0])
            return f'{ruta}: {texto}' if ruta else texto
        for index, item in enumerate(errors, start=1):
            if not item:
                continue
            siguiente = f'{ruta} {index}'.strip()
            found = mensaje_error_carga(item, siguiente)
            if found:
                return found
        return 'Los datos enviados no son válidos'

    texto = str(errors)
    return f'{ruta}: {texto}' if ruta else texto


def _mensaje_lista(errors, ruta, etiqueta):
    if isinstance(errors, (list, tuple)) and errors and not isinstance(errors[0], (dict, list)):
        texto = str(errors[0])
        return f'{ruta}: {texto}' if ruta else texto
    if not isinstance(errors, (list, tuple)):
        return mensaje_error_carga(errors, ruta)

    for index, item in enumerate(errors, start=1):
        if not item:
            continue
        parte = f'{etiqueta} {index}'
        siguiente = f'{ruta}, {parte}' if ruta else parte
        found = mensaje_error_carga(item, siguiente)
        if found:
            return found
    return 'Los datos enviados no son válidos'
