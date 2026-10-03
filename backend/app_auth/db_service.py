"""
Service layer for executing stored procedures on the GENERAL database.
"""

import pyodbc
from django.conf import settings


def _get_connection():
    """Create a direct pyodbc connection to the GENERAL database."""
    db_config = settings.DATABASES['default']
    conn_str = (
            f"DRIVER={{{db_config['OPTIONS']['driver']}}};"
            f"SERVER={db_config['HOST']};"
            f"PORT={db_config['PORT']};"
            f"DATABASE={db_config['NAME']};"
            f"UID={db_config['USER']};"
            f"PWD={db_config['PASSWORD']};"
            f"TDS_Version=7.3;"
            f"Encryption=off;"
        )
    return pyodbc.connect(conn_str)


def validate_user(login: str, password: str) -> dict:
    """
    Execute S07ValidarUsuario2 to validate user credentials.

    Returns:
        dict with keys: 'estado', 'login', 'nombre'
        On success: estado='OK', login='MMEDINA', nombre='MARIO...'
        On failure: estado='Contraseña Incorrecta' (or other error message)
    """
    system_code = settings.SYSTEM_CODE
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "EXEC S07ValidarUsuario2 @C_Usuari_Login=?, @ClaveAConsultar=?, @C_Sistema=?",
            (login, password, system_code)
        )
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
            return {
                'estado': result.get('estado', '').strip(),
                'login': result.get('Login', '').strip(),
                'nombre': result.get('Nombre', '').strip(),
            }
        return {'estado': 'Error', 'login': '', 'nombre': ''}
    finally:
        conn.close()


def get_user_menus(login: str) -> list:
    """
    Execute S07LeerUserMenues to get user menu permissions.

    Returns:
        list of dicts with menu permissions for the system.
    """
    system_code = settings.SYSTEM_CODE
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "EXEC S07LeerUserMenues @USUCODI=?, @SYSCODI=?, @Opcion=?",
            (login, system_code, '02')
        )
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def change_user_password(login: str, new_password: str) -> None:
    """
    Execute S07ModificarClaveUsuario to change user password.

    Raises:
        Exception if the stored procedure fails.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "EXEC S07ModificarClaveUsuario @Login=?, @ClaveNueva=?",
            (login, new_password)
        )
        conn.commit()
    finally:
        conn.close()

