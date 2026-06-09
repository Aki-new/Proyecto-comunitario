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
