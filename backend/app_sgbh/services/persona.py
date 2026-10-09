from django.db import transaction

from ..db_router import DB_ALIAS
from ..models import Persona, TipoDocumento

_USUARIO_LOGIN_MAX_LENGTH = 20
_NUMERO_DOCUMENTO_MAX_LENGTH = 20


class PersonaServiceError(Exception):
    """Business rule violation for a persona operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class PersonaService:
    @staticmethod
    def create(
        *,
        apellido_paterno,
        apellido_materno,
        nombres,
        fecha_nacimiento,
        sexo,
        telefono,
        correo,
        c_usuari_login,
        tipo_documento_id=None,
        numero_documento=None,
        esta_activo=True,
    ):
        """Insert one row in S43personas.

        tipo_documento_id and numero_documento must both be empty or both
        have a value, matching CK_personas_documento. When a document is
        sent, tipo_documento_id must exist in S43cat_tipos_documento and
        that pair must not already exist. The combination of
        apellido_paterno, apellido_materno, nombres and fecha_nacimiento
        must not already exist. Text is compared without case sensitivity.
        Personas without a document do not conflict with each other on the
        document pair.
        c_usuari_login comes from the authenticated user.
        esta_activo defaults to true. fecha_modificacion stays empty.
        """
        login = str(c_usuari_login or '').strip()
        if login == '' or len(login) > _USUARIO_LOGIN_MAX_LENGTH:
            raise PersonaServiceError('No se pudo identificar al usuario')

        numero_documento = _require_documento(tipo_documento_id, numero_documento)
        apellido_paterno = _require_text(apellido_paterno, 'apellido_paterno', 50)
        apellido_materno = _require_text(apellido_materno, 'apellido_materno', 50)
        nombres = _require_text(nombres, 'nombres', 150)
        sexo = _require_sexo(sexo)
        telefono = _require_text(telefono, 'telefono', 50)
        correo = _require_text(correo, 'correo', 50)
        if esta_activo is None:
            esta_activo = True

        with transaction.atomic(using=DB_ALIAS):
            if tipo_documento_id is not None:
                _require_tipo_documento(tipo_documento_id)
                _require_documento_disponible(tipo_documento_id, numero_documento)
            _require_identidad_disponible(
                apellido_paterno,
                apellido_materno,
                nombres,
                fecha_nacimiento,
            )

            persona = Persona(
                tipo_documento_id=tipo_documento_id,
                numero_documento=numero_documento,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                nombres=nombres,
                fecha_nacimiento=fecha_nacimiento,
                sexo=sexo,
                telefono=telefono,
                correo=correo,
                esta_activo=esta_activo,
                c_usuari_login=login,
            )
            persona.save()

            stored = Persona.objects.select_related('tipo_documento').get(pk=persona.pk)
        return stored


def _require_text(value, field, max_length):
    text = str(value or '').strip()
    if text == '':
        raise PersonaServiceError(f'El campo {field} es obligatorio')
    if len(text) > max_length:
        raise PersonaServiceError(
            f'El campo {field} no debe superar {max_length} caracteres'
        )
    return text


def _require_sexo(value):
    sexo = _require_text(value, 'sexo', 1)
    if len(sexo) != 1:
        raise PersonaServiceError('El campo sexo debe tener 1 carácter')
    return sexo


def _require_documento(tipo_documento_id, numero_documento):
    """Return the document number, or None when both document fields are empty."""
    numero = None if numero_documento is None else str(numero_documento).strip()
    if numero == '':
        numero = None
    if (tipo_documento_id is None) != (numero is None):
        raise PersonaServiceError(
            'Los campos tipo_documento_id y numero_documento deben enviarse juntos o ambos vacíos'
        )
    if numero is not None and len(numero) > _NUMERO_DOCUMENTO_MAX_LENGTH:
        raise PersonaServiceError(
            'El campo numero_documento no debe superar 20 caracteres'
        )
    return numero


def _require_tipo_documento(tipo_documento_id):
    if not TipoDocumento.objects.filter(pk=tipo_documento_id).exists():
        raise PersonaServiceError('El tipo de documento indicado no existe')


def _require_documento_disponible(tipo_documento_id, numero_documento):
    """Reject a document pair that another persona already uses."""
    if Persona.objects.filter(
        tipo_documento_id=tipo_documento_id,
        numero_documento__iexact=numero_documento,
    ).exists():
        raise PersonaServiceError(
            'Ya existe una persona con el tipo y número de documento indicados',
            conflict=True,
        )


def _require_identidad_disponible(
    apellido_paterno,
    apellido_materno,
    nombres,
    fecha_nacimiento,
):
    """Reject the same surnames, given names and birth date."""
    if Persona.objects.filter(
        apellido_paterno__iexact=apellido_paterno,
        apellido_materno__iexact=apellido_materno,
        nombres__iexact=nombres,
        fecha_nacimiento=fecha_nacimiento,
    ).exists():
        raise PersonaServiceError(
            'Ya existe una persona con los mismos apellidos, nombres y fecha de nacimiento',
            conflict=True,
        )
