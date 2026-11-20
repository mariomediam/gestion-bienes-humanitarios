import logging
import uuid
from pathlib import Path

from auditlog.context import disable_auditlog
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from ..db_router import DB_ALIAS
from ..models import Movimiento, MovimientoArchivo

logger = logging.getLogger(__name__)

_NOMBRE_MAX = 255
_EXTENSION_MAX = 10
_RUTA_MAX = 500
_USUARIO_LOGIN_MAX_LENGTH = 20


class MovimientoArchivoServiceError(Exception):
    """Business rule violation for a warehouse movement file operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class MovimientoArchivoService:
    @staticmethod
    def search(archivo_id=None, movimiento_id=None, esta_activo=None):
        """Return file rows using optional filters combined with AND.

        All filters are exact. With no filters, every row is returned.
        Ordered by fecha_registro ascending, the same order as
        ORDER BY fecha_registro. Each row includes the parent movement
        so the response can expose almacen_id and documento_referencia.
        """
        queryset = MovimientoArchivo.objects.select_related('movimiento')
        if archivo_id is not None:
            queryset = queryset.filter(archivo_id=archivo_id)
        if movimiento_id is not None:
            queryset = queryset.filter(movimiento_id=movimiento_id)
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)
        return queryset.order_by('fecha_registro')

    @staticmethod
    def create(*, movimiento_id, archivo, c_usuari_login):
        """Store one digital file and insert its S43alm_movimientos_archivos row.

        The parent movement must exist. The bytes go under STORAGE_ROOT.
        The database stores the original name, the generated file name,
        the relative path, the extension and the size. c_usuari_login is
        the authenticated login. esta_activo and fecha_registro use the
        model defaults. When the insert fails, the stored file is removed.

        The audit row lives on GENERAL. It is written after the SIAC
        transaction commits. Doing it inside the same atomic block leaves
        the archivo insert uncommitted while GENERAL runs SET ARITHABORT.
        A lock on GENERAL then keeps the request at 100% and, when that
        session is killed, rolls the insert back. The file stays on disk
        and the table stays empty.
        """
        login = _require_login(c_usuari_login)
        nombre_original, extension = _require_upload(archivo)
        nombre_archivo = f'{uuid.uuid4().hex}.{extension}'
        ruta_archivo = f'movimientos/{movimiento_id}/{nombre_archivo}'
        if len(nombre_archivo) > _NOMBRE_MAX or len(ruta_archivo) > _RUTA_MAX:
            raise MovimientoArchivoServiceError('No se pudo almacenar el archivo')

        destination = _destination(ruta_archivo)
        try:
            with transaction.atomic(using=DB_ALIAS):
                _require_movimiento(movimiento_id)
                _write_upload(destination, archivo)
                row = MovimientoArchivo(
                    movimiento_id=movimiento_id,
                    nombre_original=nombre_original,
                    nombre_archivo=nombre_archivo,
                    ruta_archivo=ruta_archivo,
                    extension=extension,
                    tamano_bytes=archivo.size,
                    c_usuari_login=login,
                )
                with disable_auditlog():
                    row.save()
                stored = MovimientoArchivo.objects.get(pk=row.pk)
        except Exception:
            _delete_file(destination)
            raise
        _record_create(stored)
        return stored

    @staticmethod
    def delete(movimiento_id, archivo_id):
        """Mark one S43alm_movimientos_archivos row inactive.

        The row and the file on disk stay in place. esta_activo becomes
        false. Rejected when the file does not belong to the movement
        or is already inactive.
        """
        with transaction.atomic(using=DB_ALIAS):
            archivo = _require_archivo(movimiento_id, archivo_id)
            if not archivo.esta_activo:
                raise MovimientoArchivoServiceError(
                    'El archivo indicado ya está inactivo',
                    conflict=True,
                )
            archivo.esta_activo = False
            archivo.save(update_fields=['esta_activo'])

    @staticmethod
    def download(movimiento_id, archivo_id):
        """Return the stored file so the view can stream it.

        The row must belong to the movement. An inactive row can still
        be downloaded: the logical delete keeps the bytes on disk.
        The resolved path must stay inside STORAGE_ROOT. The caller
        receives the path only to open it; the HTTP response uses the
        original name and never the internal path.
        """
        archivo = _require_archivo_lectura(movimiento_id, archivo_id)
        path = _safe_stored_file(archivo.ruta_archivo)
        return MovimientoArchivoDownload(
            path=path,
            filename=_download_filename(
                archivo.nombre_original,
                archivo.nombre_archivo,
            ),
            content_type=_content_type(archivo.extension),
        )


class MovimientoArchivoDownload:
    """File the view streams. path stays on the server."""

    def __init__(self, path, filename, content_type):
        self.path = path
        self.filename = filename
        self.content_type = content_type


_CONTENT_TYPES = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}


def _record_create(instance):
    """Write the GENERAL audit row for one archivo that is already committed.

    A failure here must not remove the file or the SIAC row. The caller
    has already committed both.
    """
    try:
        from auditlog.receivers import log_create

        log_create(sender=type(instance), instance=instance, created=True)
    except Exception:
        logger.exception(
            'No se pudo registrar la auditoría del archivo %s del movimiento %s',
            getattr(instance, 'pk', None),
            getattr(instance, 'movimiento_id', None),
        )


def _require_login(c_usuari_login):
    """Return the token login stored in c_usuari_login."""
    login = str(c_usuari_login or '').strip()
    if login == '' or len(login) > _USUARIO_LOGIN_MAX_LENGTH:
        raise MovimientoArchivoServiceError('No se pudo identificar al usuario')
    return login


def _require_upload(archivo):
    """Return (nombre_original, extension) for one uploaded file."""
    if not isinstance(archivo, UploadedFile):
        raise MovimientoArchivoServiceError('El archivo es obligatorio')

    size = archivo.size
    if size is None or size < 1:
        raise MovimientoArchivoServiceError('El archivo está vacío')
    if size > _max_upload_bytes():
        raise MovimientoArchivoServiceError(
            'El archivo supera el tamaño máximo permitido'
        )

    nombre_original = _basename(getattr(archivo, 'name', ''))
    if not nombre_original or nombre_original in {'.', '..'}:
        raise MovimientoArchivoServiceError('El archivo no tiene un nombre válido')
    if any(ord(char) < 32 for char in nombre_original):
        raise MovimientoArchivoServiceError('El archivo no tiene un nombre válido')
    if len(nombre_original) > _NOMBRE_MAX:
        raise MovimientoArchivoServiceError(
            'El nombre del archivo no puede superar 255 caracteres'
        )

    base, dot, extension = nombre_original.rpartition('.')
    extension = extension.lower()
    if not dot:
        raise MovimientoArchivoServiceError('El archivo debe tener una extensión')
    if not base:
        raise MovimientoArchivoServiceError('El archivo no tiene un nombre válido')
    if not extension.isalnum() or len(extension) > _EXTENSION_MAX:
        raise MovimientoArchivoServiceError('El archivo debe tener una extensión')
    permitidas = _allowed_extensions()
    if extension not in permitidas:
        aceptadas = ', '.join(sorted(permitidas))
        raise MovimientoArchivoServiceError(
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


def _safe_stored_file(ruta_archivo):
    """Resolve ruta_archivo under STORAGE_ROOT and require a regular file."""
    raw = str(ruta_archivo or '').replace('\\', '/').strip()
    if not raw or raw.startswith('/') or ':' in raw:
        raise MovimientoArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        )
    parts = [part for part in raw.split('/') if part not in ('', '.')]
    if not parts or any(part == '..' for part in parts):
        raise MovimientoArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        )

    root = Path(settings.STORAGE_ROOT).resolve()
    destination = root.joinpath(*parts).resolve()
    if destination != root and root not in destination.parents:
        raise MovimientoArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        )
    if not destination.is_file():
        raise MovimientoArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        )
    return destination


def _download_filename(nombre_original, nombre_archivo):
    """Name sent to the browser. Falls back when the original is unsafe."""
    for candidate in (nombre_original, nombre_archivo):
        name = _basename(candidate)
        if (
            name
            and name not in {'.', '..'}
            and len(name) <= _NOMBRE_MAX
            and all(ord(char) >= 32 for char in name)
        ):
            return name
    return 'archivo'


def _content_type(extension):
    return _CONTENT_TYPES.get(
        str(extension or '').strip().lower().lstrip('.'),
        'application/octet-stream',
    )


def _require_archivo_lectura(movimiento_id, archivo_id):
    try:
        return MovimientoArchivo.objects.get(
            pk=archivo_id,
            movimiento_id=movimiento_id,
        )
    except MovimientoArchivo.DoesNotExist:
        raise MovimientoArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        ) from None


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


def _require_archivo(movimiento_id, archivo_id):
    try:
        return MovimientoArchivo.objects.select_for_update().get(
            pk=archivo_id,
            movimiento_id=movimiento_id,
        )
    except MovimientoArchivo.DoesNotExist:
        raise MovimientoArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        ) from None


def _require_movimiento(movimiento_id):
    try:
        return Movimiento.objects.select_for_update().get(pk=movimiento_id)
    except Movimiento.DoesNotExist:
        raise MovimientoArchivoServiceError(
            'El movimiento de almacén indicado no existe',
            not_found=True,
        ) from None
