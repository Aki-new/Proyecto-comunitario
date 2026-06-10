"""
Script de inicialización (seed) para la base de datos de SGI Salud.
Crea la base de datos limpia con los datos mínimos esenciales de operación
(colores, servicios por defecto, usuario administrador inicial).

Ejecutar desde la raíz del proyecto:
    python seed.py
"""

import os
import sys
import sqlite3
import hashlib
from src.utils.date_utils import normalizar_fecha_a_iso

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")
SQL_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# ── Los 10 colores oficiales del hospital ─────────────────────────
COLORES_HOSPITAL = [
    "Marron",        # 00-09
    "Azul Marino",   # 10-19
    "Verde",         # 20-29
    "Naranja",       # 30-39
    "Morado",        # 40-49
    "Rosa",          # 50-59
    "Turquesa",      # 60-69
    "Amarillo",      # 70-79
    "Rojo",          # 80-89
    "Azul Celeste",  # 90-99
]

# ── Servicios hospitalarios por defecto ───────────────────────────
SERVICIOS_HOSPITAL = [
    ("Obstetricia", 20),
    ("Cirugía", 8),
    ("Medicina", 8),
    ("Pediatría", 13),
    ("Emergencia Médica", 8),
    ("Emergencia Pediátrica", 9),
]


def hash_clave(clave: str) -> str:
    """Genera hash SHA-256 (mismo método que UsuarioDAO)."""
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def inicializar_esquema(conn: sqlite3.Connection):
    """Ejecuta el archivo schema.sql para inicializar las tablas de la BD."""
    if os.path.exists(SQL_PATH):
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            sql = f.read()
        try:
            conn.executescript(sql)
            print("[OK] Esquema de base de datos inicializado.")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print(f"  [INFO] Esquema ya existente, continuando... ({e})")
            else:
                raise
    else:
        print(f"[ERROR] No se encontró el archivo de esquema: {SQL_PATH}")
        sys.exit(1)


def insertar_colores(conn: sqlite3.Connection):
    """Inserta los 10 colores oficiales requeridos por las tarjetas."""
    cursor = conn.cursor()
    for color in COLORES_HOSPITAL:
        cursor.execute("SELECT id FROM colores WHERE valor = ?", (color,))
        if cursor.fetchone():
            print(f"  [SKIP] Color '{color}' ya existe.")
        else:
            cursor.execute(
                "INSERT INTO colores (valor, estado) VALUES (?, 1)", (color,)
            )
            print(f"  [OK] Color '{color}' creado.")


def insertar_usuario(conn: sqlite3.Connection, nombre, apellido, cedula, usuario, clave):
    """Inserta el usuario inicial si no existe en la base de datos."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
    if cursor.fetchone():
        print(f"  [SKIP] Usuario '{usuario}' ya existe.")
        return

    clave_hash = hash_clave(clave)
    cursor.execute(
        "INSERT INTO usuarios (nombre, apellido, cedula, usuario, clave, estado) "
        "VALUES (?, ?, ?, ?, ?, 1)",
        (nombre, apellido, cedula, usuario, clave_hash),
    )
    print(f"  [OK] Usuario '{usuario}' creado.")


def insertar_servicios(conn: sqlite3.Connection):
    """Inserta los servicios y capacidades por defecto del tarjetero."""
    cursor = conn.cursor()
    for nombre, camas in SERVICIOS_HOSPITAL:
        cursor.execute("SELECT id FROM servicios WHERE nombre = ?", (nombre,))
        if cursor.fetchone():
            print(f"  [SKIP] Servicio '{nombre}' ya existe.")
        else:
            cursor.execute(
                "INSERT INTO servicios (nombre, total_camas, estado) VALUES (?, ?, 1)",
                (nombre, camas),
            )
            print(f"  [OK] Servicio '{nombre}' ({camas} camas) creado.")


def obtener_id_color(conn: sqlite3.Connection, valor: str) -> int | None:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM colores WHERE valor = ? AND estado = 1",
        (valor,),
    )
    fila = cursor.fetchone()
    if fila:
        return fila[0]

    cursor.execute("SELECT id FROM colores WHERE estado = 1 ORDER BY id LIMIT 1")
    fallback = cursor.fetchone()
    return fallback[0] if fallback else None


def paciente_existe(conn: sqlite3.Connection, datos: dict) -> bool:
    cursor = conn.cursor()
    cedula = datos["cedula"].strip().upper()
    if cedula and cedula != "S/C":
        cursor.execute(
            "SELECT 1 FROM pacientes WHERE cedula = ? AND estado = 1",
            (cedula,),
        )
        return cursor.fetchone() is not None

    cursor.execute(
        "SELECT 1 FROM pacientes WHERE nombre1 = ? AND COALESCE(nombre2, '') = ? "
        "AND apellido1 = ? AND COALESCE(apellido2, '') = ? "
        "AND lugar_nacimiento = ? AND fecha_nacimiento = ? AND estado = 1",
        (
            datos["nombre1"].strip(),
            datos.get("nombre2", "") or "",
            datos["apellido1"].strip(),
            datos.get("apellido2", "") or "",
            datos["lugar_nacimiento"].strip(),
            datos["fecha_nacimiento"],
        ),
    )
    return cursor.fetchone() is not None


def tarjeta_existe(conn: sqlite3.Connection, num_historia: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM tarjetas WHERE num_historia = ? AND estado = 1",
        (num_historia,),
    )
    return cursor.fetchone() is not None


def insertar_pacientes(conn: sqlite3.Connection):
    """Inserta pacientes de ejemplo con tarjetas en formato correcto."""
    motor = [
        {
            "cedula": "V-12345678",
            "nombre1": "Alejandro",
            "nombre2": "José",
            "apellido1": "González",
            "apellido2": "Pérez",
            "lugar_nacimiento": "Caracas",
            "fecha_nacimiento": "15/09/1985",
            "estado_vital": 1,
            "num_historia": "22-10-81",
            "color": "Rojo",
        },
        {
            "cedula": "E-87654321",
            "nombre1": "María",
            "nombre2": "Fernanda",
            "apellido1": "López",
            "apellido2": "Martínez",
            "lugar_nacimiento": "Valencia",
            "fecha_nacimiento": "07-04-1990",
            "estado_vital": 1,
            "num_historia": "05-32-92",
            "color": "Azul Celeste",
        },
        {
            "cedula": "V-40234567",
            "nombre1": "Carlos",
            "nombre2": "Miguel",
            "apellido1": "Ramírez",
            "apellido2": "Delgado",
            "lugar_nacimiento": "Maracaibo",
            "fecha_nacimiento": "1998-12-01",
            "estado_vital": 0,
            "num_historia": "03-27-45",
            "color": "Naranja",
        },
        {
            "cedula": "S/C",
            "nombre1": "Ana",
            "nombre2": None,
            "apellido1": "Martínez",
            "apellido2": "López",
            "lugar_nacimiento": "Ciudad Bolívar",
            "fecha_nacimiento": "10/06/2021",
            "estado_vital": 1,
            "num_historia": "11-06-71",
            "color": "Amarillo",
        },
        {
            "cedula": "V-55011234",
            "nombre1": "Lorena",
            "nombre2": "Isabel",
            "apellido1": "Sánchez",
            "apellido2": "Guerra",
            "lugar_nacimiento": "Barquisimeto",
            "fecha_nacimiento": "25-11-1982",
            "estado_vital": 1,
            "num_historia": "09-18-60",
            "color": "Turquesa",
        },
    ]

    cursor = conn.cursor()
    for paciente in motor:
        try:
            paciente["fecha_nacimiento"] = normalizar_fecha_a_iso(paciente["fecha_nacimiento"])
        except ValueError as e:
            print(f"  [ERROR] Fecha invalida para paciente {paciente['nombre1']} {paciente['apellido1']}: {e}")
            continue

        if tarjeta_existe(conn, paciente["num_historia"]):
            print(f"  [SKIP] Tarjeta '{paciente['num_historia']}' ya existe.")
            continue

        if paciente_existe(conn, paciente):
            print(f"  [SKIP] Paciente '{paciente['nombre1']} {paciente['apellido1']}' ya existe.")
            continue

        cedula_db = None if paciente["cedula"].strip().upper() == "S/C" else paciente["cedula"].strip().upper()
        cursor.execute(
            "INSERT INTO pacientes (cedula, nombre1, nombre2, apellido1, apellido2, "
            "lugar_nacimiento, fecha_nacimiento, estado_vital, estado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (
                cedula_db,
                paciente["nombre1"].strip(),
                paciente.get("nombre2"),
                paciente["apellido1"].strip(),
                paciente.get("apellido2"),
                paciente["lugar_nacimiento"].strip(),
                paciente["fecha_nacimiento"],
                paciente["estado_vital"],
            ),
        )
        paciente_id = cursor.lastrowid
        id_color = obtener_id_color(conn, paciente["color"])
        if id_color is None:
            print(f"  [ERROR] Color no encontrado para tarjeta '{paciente['num_historia']}'.")
            conn.rollback()
            continue

        cursor.execute(
            "INSERT INTO tarjetas (num_historia, id_paciente, id_color, estado) "
            "VALUES (?, ?, ?, 1)",
            (paciente["num_historia"], paciente_id, id_color),
        )
        print(f"  [OK] Paciente '{paciente['nombre1']} {paciente['apellido1']}' creado con tarjeta {paciente['num_historia']}." )

    conn.commit()


def main():
    print("=" * 50)
    print("  SEED -- Inicialización Limpia de Base de Datos")
    print("=" * 50)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    try:
        print("\n> Inicializando esquema...")
        inicializar_esquema(conn)

        print("\n> Insertando colores del hospital (10 colores)...")
        insertar_colores(conn)

        print("\n> Insertando usuario Administrador inicial...")
        insertar_usuario(conn, "Admin", "Sistema", 99999999, "admin", "admin123")

        print("\n> Insertando servicios hospitalarios por defecto...")
        insertar_servicios(conn)

        print("\n> Insertando pacientes de ejemplo con tarjetas...")
        insertar_pacientes(conn)

        conn.commit()
        print("\n" + "=" * 50)
        print("  [OK] Inicialización completada exitosamente")
        print("=" * 50)
        print("\n  Credenciales de administración iniciales:")
        print("  +--------------+--------------+")
        print("  | Usuario      | Clave        |")
        print("  +--------------+--------------+")
        print("  | admin        | admin123     |")
        print("  +--------------+--------------+")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
