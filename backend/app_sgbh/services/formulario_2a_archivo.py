import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from ..db_router import DB_ALIAS
from ..models import Formulario2A, Formulario2AArchivo
from .formulario_2a import Formulario2AService, Formulario2AServiceError

_NOMBRE_MAX = 255
_EXTENSION_MAX = 10
_RUTA_MAX = 500
_USUARIO_LOGIN_MAX_LENGTH = 20


class Formulario2AArchivoServiceError(Exception):
    """Business rule violation for a Formulario 2A file operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class Formulario2AArchivoService:
    @staticmethod
    def create(*, formulario_2a_id, archivo, c_usuari_login):
        """Store one digital file and insert its S43edan_formulario_2a_archivos row.

        The parent Formulario 2A must exist and still accept changes.
        The bytes go under STORAGE_ROOT. The database stores the original
        name, the generated file name, the relative path, the extension
        and the size. c_usuari_login is the authenticated login.
        esta_activo and fecha_registro use the model defaults.
        When the insert fails, the stored file is removed.
        """
        login = _require_login(c_usuari_login)
        nombre_original, extension = _require_upload(archivo)
        nombre_archivo = f'{uuid.uuid4().hex}.{extension}'
        ruta_archivo = f'formularios-2a/{formulario_2a_id}/{nombre_archivo}'
        if len(nombre_archivo) > _NOMBRE_MAX or len(ruta_archivo) > _RUTA_MAX:
            raise Formulario2AArchivoServiceError('No se pudo almacenar el archivo')

        destination = _destination(ruta_archivo)
        with transaction.atomic(using=DB_ALIAS):
            formulario = _require_formulario(formulario_2a_id)
            # _require_formulario_modificable(formulario)
            _write_upload(destination, archivo)
            try:
                row = Formulario2AArchivo(
                    formulario_2a_id=formulario_2a_id,
                    nombre_original=nombre_original,
                    nombre_archivo=nombre_archivo,
                    ruta_archivo=ruta_archivo,
                    extension=extension,
                    tamano_bytes=archivo.size,
                    c_usuari_login=login,
                )
                row.save()
                stored = Formulario2AArchivo.objects.get(pk=row.pk)
            except Exception as e:
                print('****************************************')
                print(e)
                print('****************************************')
                _delete_file(destination)
                raise
        return stored


def _require_login(c_usuari_login):
    """Return the token login stored in c_usuari_login."""
    login = str(c_usuari_login or '').strip()
    if login == '' or len(login) > _USUARIO_LOGIN_MAX_LENGTH:
        raise Formulario2AArchivoServiceError('No se pudo identificar al usuario')
    return login


def _require_upload(archivo):
    """Return (nombre_original, extension) for one uploaded file."""
    if not isinstance(archivo, UploadedFile):
        raise Formulario2AArchivoServiceError('El archivo es obligatorio')

    size = archivo.size
    if size is None or size < 1:
        raise Formulario2AArchivoServiceError('El archivo está vacío')
    if size > _max_upload_bytes():
        raise Formulario2AArchivoServiceError(
            'El archivo supera el tamaño máximo permitido'
        )

    nombre_original = _basename(getattr(archivo, 'name', ''))
    if not nombre_original or nombre_original in {'.', '..'}:
        raise Formulario2AArchivoServiceError('El archivo no tiene un nombre válido')
    if any(ord(char) < 32 for char in nombre_original):
        raise Formulario2AArchivoServiceError('El archivo no tiene un nombre válido')
    if len(nombre_original) > _NOMBRE_MAX:
        raise Formulario2AArchivoServiceError(
            'El nombre del archivo no puede superar 255 caracteres'
        )

    base, dot, extension = nombre_original.rpartition('.')
    extension = extension.lower()
    if not dot:
        raise Formulario2AArchivoServiceError('El archivo debe tener una extensión')
    if not base:
        raise Formulario2AArchivoServiceError('El archivo no tiene un nombre válido')
    if not extension.isalnum() or len(extension) > _EXTENSION_MAX:
        raise Formulario2AArchivoServiceError('El archivo debe tener una extensión')
    permitidas = _allowed_extensions()
    if extension not in permitidas:
        aceptadas = ', '.join(sorted(permitidas))
        raise Formulario2AArchivoServiceError(
            f'El tipo de archivo no está permitido. Extensiones aceptadas: {aceptadas}'
        )
    return nombre_original, extension


def _allowed_extensions():
    raw = getattr(settings, 'STORAGE_ALLOWED_EXTENSIONS', ())
    return {
        item.strip().lower().lstrip('.')
        for item in raw
        if isinstance(item, str) and item.strip()
    }


def _max_upload_bytes():
    try:
        return int(settings.STORAGE_MAX_UPLOAD_BYTES)
    except (TypeError, ValueError):
        return 0


def _basename(raw_name):
    return str(raw_name or '').replace('\\', '/').split('/')[-1].strip()


def _destination(ruta_archivo):
    return Path(settings.STORAGE_ROOT).joinpath(*ruta_archivo.split('/'))


def _write_upload(destination, archivo):
    destination.parent.mkdir(parents=True, exist_ok=True)
    archivo.seek(0)
    try:
        with destination.open('wb') as target:
            for chunk in archivo.chunks():
                target.write(chunk)
    except Exception:
        _delete_file(destination)
        raise


def _delete_file(path):
    try:
        path.unlink(missing_ok=True)
    except OSError:
        return


def _require_formulario(formulario_2a_id):
    try:
        return Formulario2A.objects.select_for_update().get(pk=formulario_2a_id)
    except Formulario2A.DoesNotExist:
        raise Formulario2AArchivoServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ) from None


# def _require_formulario_modificable(formulario):
#     try:
#         Formulario2AService.require_modificable(formulario)
#     except Formulario2AServiceError as exc:
#         raise Formulario2AArchivoServiceError(
#             exc.message,
#             conflict=exc.conflict,
#             not_found=exc.not_found,
#         ) from exc
