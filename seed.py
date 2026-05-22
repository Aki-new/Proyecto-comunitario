"""
Script de seed para insertar datos de prueba en la base de datos.
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


def hash_clave(clave: str) -> str:
    """Genera hash SHA-256 (mismo método que UsuarioDAO)."""
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def inicializar_esquema(conn: sqlite3.Connection):
    """Ejecuta el schema.sql si existe.
    Tolera objetos ya existentes (tablas, vistas, índices).
    """
    if os.path.exists(SQL_PATH):
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            sql = f.read()
        try:
            conn.executescript(sql)
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print(f"  [INFO] Esquema ya existente, continuando... ({e})")
            else:
                raise
        print("[OK] Esquema verificado.")
    else:
        print(f"[ERROR] No se encontro el archivo de esquema: {SQL_PATH}")
        sys.exit(1)


def insertar_usuario(conn: sqlite3.Connection, nombre, apellido, cedula, usuario, clave):
    """Inserta un usuario si no existe previamente."""
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
    print(f"  [OK] Usuario '{usuario}' creado (clave: {clave}).")


def insertar_colores(conn: sqlite3.Connection):
    """Inserta colores básicos de clasificación si no existen."""
    colores = ["Rojo", "Azul", "Verde", "Amarillo", "Blanco"]
    cursor = conn.cursor()
    for color in colores:
        cursor.execute("SELECT id FROM colores WHERE valor = ?", (color,))
        if cursor.fetchone():
            print(f"  [SKIP] Color '{color}' ya existe.")
        else:
            cursor.execute(
                "INSERT INTO colores (valor, estado) VALUES (?, 1)", (color,)
            )
            print(f"  [OK] Color '{color}' creado.")


def insertar_pacientes_prueba(conn: sqlite3.Connection):
    """Inserta pacientes de ejemplo con sus tarjetas."""
    cursor = conn.cursor()

    pacientes = [
        ("V-12345678", "María",  "Elena",   "González", "Pérez",   "Barquisimeto", "1985-03-15", 1),
        ("V-87654321", "Carlos", "Alberto", "Rodríguez", "López",  "Cabudare",     "1990-07-22", 1),
        ("V-11223344", "Ana",    None,      "Martínez",  "García", "Barquisimeto", "1978-11-08", 1),
    ]

    for pac in pacientes:
        cedula = pac[0]
        cursor.execute("SELECT id FROM pacientes WHERE cedula = ?", (cedula,))
        if cursor.fetchone():
            print(f"  [SKIP] Paciente '{cedula}' ya existe.")
            continue

        cursor.execute(
            "INSERT INTO pacientes "
            "(cedula, nombre1, nombre2, apellido1, apellido2, "
            " lugar_nacimiento, fecha_nacimiento, estado_vital, estado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            pac,
        )
        id_paciente = cursor.lastrowid
        print(f"  [OK] Paciente '{cedula}' creado (ID: {id_paciente}).")

    # Obtener id del primer color para las tarjetas
    cursor.execute("SELECT id FROM colores WHERE estado = 1 LIMIT 1")
    fila_color = cursor.fetchone()
    if not fila_color:
        print("  [WARN] No hay colores disponibles. Tarjetas no creadas.")
        return
    id_color = fila_color[0]

    tarjetas = [
        ("HC-001", "V-12345678"),
        ("HC-002", "V-87654321"),
        ("HC-003", "V-11223344"),
    ]

    for num_historia, cedula in tarjetas:
        cursor.execute(
            "SELECT t.id FROM tarjetas t "
            "JOIN pacientes p ON t.id_paciente = p.id "
            "WHERE p.cedula = ?",
            (cedula,),
        )
        if cursor.fetchone():
            print(f"  [SKIP] Tarjeta para '{cedula}' ya existe.")
            continue

        cursor.execute("SELECT id FROM pacientes WHERE cedula = ?", (cedula,))
        fila_pac = cursor.fetchone()
        if not fila_pac:
            continue

        cursor.execute(
            "INSERT INTO tarjetas (num_historia, id_paciente, id_color, estado) "
            "VALUES (?, ?, ?, 1)",
            (num_historia, fila_pac[0], id_color),
        )
        print(f"  [OK] Tarjeta '{num_historia}' creada para '{cedula}'.")


def main():
    print("=" * 50)
    print("  SEED — Datos de prueba")
    print("=" * 50)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    try:
        print("\n> Inicializando esquema...")
        inicializar_esquema(conn)

        print("\n> Insertando usuarios...")
        insertar_usuario(conn, "Admin", "Sistema", 99999999, "admin", "admin123")
        insertar_usuario(conn, "Juan",  "Pérez",   12345678, "jperez", "1234")

        print("\n> Insertando colores...")
        insertar_colores(conn)

        print("\n> Insertando pacientes de prueba...")
        insertar_pacientes_prueba(conn)

        conn.commit()
        print("\n" + "=" * 50)
        print("  [OK] Seed completado exitosamente")
        print("=" * 50)
        print("\n  Credenciales de prueba:")
        print("  +--------------+--------------+")
        print("  | Usuario      | Clave        |")
        print("  +--------------+--------------+")
        print("  | admin        | admin123     |")
        print("  | jperez       | 1234         |")
        print("  +--------------+--------------+")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
