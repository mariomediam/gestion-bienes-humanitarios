"""
Service layer for executing stored procedures on the GENERAL database.
"""

import pyodbc
from django.conf import settings


def _get_connection():
    """Create a direct pyodbc connection to the GENERAL database.

    autocommit matches SSMS: each stored procedure confirms its own writes.
    These procedures record side effects (for example login audit) and were
    written for clients that do not wrap the call in an outer transaction.
    """
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
    return pyodbc.connect(conn_str, autocommit=True)


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
    finally:
        conn.close()



def get_user_menu_access(login: str, men_codi: str) -> dict | None:
    """Return permissions for one menu, or None when the user has no row."""
    codigo = str(men_codi).strip()
    for menu in get_user_menus(login):
        if str(menu.get('MenCodi', '')).strip() == codigo:
            return _normalizar_acceso(menu)
    return None


def _normalizar_acceso(menu: dict) -> dict:

    def activo(valor):
        return bool(valor)

    return {
        'men_codi': str(menu.get('MenCodi', '')).strip(),
        'consultar': True,
        'nuevo': activo(menu.get('Nuevo')), 
        'modificar': activo(menu.get('Modificar')),
        'eliminar': activo(menu.get('Eliminar')),
        'imprimir': activo(menu.get('Imprimir')),
    }