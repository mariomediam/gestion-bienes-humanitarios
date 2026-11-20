"""Move datetimes that were stored as UTC wall time to America/Lima.

SQL Server keeps the clock and drops the offset. While the application
converted aware values to UTC, fecha_creacion, fecha_modificacion,
fecha_registro and the other S43 datetimes were saved five hours ahead
of the local clock. auditlog_logentry.timestamp kept the offset, so its
instant was right but the visible clock was UTC.
"""

import re

from django.db import connections, migrations

OFFSET_HOURS = 5

S43_DATETIME_COLUMNS = {
    'S43personas': ('fecha_creacion', 'fecha_modificacion'),
    'S43edan_emergencias': ('fecha_creacion', 'fecha_modificacion'),
    'S43edan_formulario_2a': ('fecha_creacion', 'fecha_modificacion'),
    'S43edan_formulario_2a_viviendas': ('fecha_creacion',),
    'S43edan_formulario_2a_familias': ('fecha_creacion',),
    'S43edan_formulario_2a_integrantes': ('fecha_creacion',),
    'S43edan_formulario_2a_medios_vida': ('fecha_creacion',),
    'S43edan_formulario_2a_archivos': ('fecha_registro',),
    'S43alm_movimientos': (
        'fecha_movimiento',
        'fecha_confirmacion',
        'fecha_creacion',
        'fecha_modificacion',
    ),
    'S43alm_movimiento_detalle': ('fecha_creacion',),
    'S43alm_movimientos_archivos': ('fecha_registro',),
    'S43bah_planilla_entrega': (
        'fecha_emision',
        'fecha_anulacion',
        'fecha_creacion',
        'fecha_modificacion',
    ),
}

_IDENTIFIER = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def _quote(name):
    if not _IDENTIFIER.match(name):
        raise ValueError(f'Identificador SQL no permitido: {name}')
    return f'[{name}]'


def _timestamp_type(cursor):
    cursor.execute(
        """
        SELECT DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = 'auditlog_logentry'
          AND COLUMN_NAME = 'timestamp'
        """
    )
    row = cursor.fetchone()
    return row[0] if row else None


def _timestamp_index(cursor):
    cursor.execute(
        """
        SELECT i.name
        FROM sys.indexes AS i
        INNER JOIN sys.index_columns AS ic
            ON ic.object_id = i.object_id
           AND ic.index_id = i.index_id
        INNER JOIN sys.columns AS c
            ON c.object_id = ic.object_id
           AND c.column_id = ic.column_id
        WHERE i.object_id = OBJECT_ID(N'dbo.auditlog_logentry')
          AND c.name = N'timestamp'
          AND i.is_primary_key = 0
          AND i.is_unique_constraint = 0
        """
    )
    row = cursor.fetchone()
    return row[0] if row else None


def _shift_audit(cursor, hours):
    """Convert the audit clock by ``hours`` and match the column type."""
    current_type = _timestamp_type(cursor)
    if current_type is None:
        return
    target_type = 'datetime2' if hours < 0 else 'datetimeoffset'
    if current_type == target_type:
        return

    index_name = _timestamp_index(cursor)
    if index_name:
        cursor.execute(
            f'DROP INDEX {_quote(index_name)} ON dbo.auditlog_logentry'
        )
    cursor.execute(
        'ALTER TABLE dbo.auditlog_logentry '
        f'ALTER COLUMN timestamp {target_type} NOT NULL'
    )
    cursor.execute(
        'UPDATE dbo.auditlog_logentry '
        'SET timestamp = DATEADD(hour, %s, timestamp)',
        [hours],
    )
    if index_name:
        cursor.execute(
            'CREATE INDEX '
            f'{_quote(index_name)} ON dbo.auditlog_logentry (timestamp)'
        )


def _shift_s43(hours):
    connection = connections['sgbh']
    with connection.cursor() as cursor:
        for table, columns in S43_DATETIME_COLUMNS.items():
            assignments = ', '.join(
                f'{_quote(column)} = DATEADD(hour, %s, {_quote(column)})'
                for column in columns
            )
            params = [hours] * len(columns)
            cursor.execute(
                f'UPDATE dbo.{_quote(table)} SET {assignments}',
                params,
            )


def forwards(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        _shift_audit(cursor, -OFFSET_HOURS)
    _shift_s43(-OFFSET_HOURS)


def backwards(apps, schema_editor):
    _shift_s43(OFFSET_HOURS)
    with schema_editor.connection.cursor() as cursor:
        _shift_audit(cursor, OFFSET_HOURS)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('app_audit', '0001_audit_log_entry'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
