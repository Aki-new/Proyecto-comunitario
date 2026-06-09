"""
Script de seed para insertar datos de prueba en la base de datos.
Ejecutar desde la raiz del proyecto:
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


def hash_clave(clave: str) -> str:
    """Genera hash SHA-256 (mismo metodo que UsuarioDAO)."""
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def inicializar_esquema(conn: sqlite3.Connection):
    """Ejecuta el schema.sql si existe."""
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


def insertar_colores(conn: sqlite3.Connection):
    """Inserta los 10 colores oficiales del hospital."""
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


def insertar_pacientes_prueba(conn: sqlite3.Connection):
    """Inserta pacientes de ejemplo con tarjetas en formato XX-XX-XX."""
    cursor = conn.cursor()

    pacientes = [
        ("V-12345678", "Maria",  "Elena",   "Gonzalez",  "Perez",   "Barquisimeto", "15/03/1985", 1),
        ("V-87654321", "Carlos", "Alberto", "Rodriguez", "Lopez",   "Cabudare",     "22/07/1990", 1),
        ("V-11223344", "Ana",    None,      "Martinez",  "Garcia",  "Barquisimeto", "08/11/1978", 1),
        (None,         "Luis",   "Miguel",  "Perez",     "Gomez",   "Barquisimeto", "10/05/2023", 1),
    ]

    for pac in pacientes:
        cedula = pac[0]
        nombre1 = pac[1]

        if cedula is not None:
            cursor.execute("SELECT id FROM pacientes WHERE cedula = ?", (cedula,))
        else:
            cursor.execute(
                "SELECT id FROM pacientes WHERE cedula IS NULL AND nombre1 = ?",
                (nombre1,))
        if cursor.fetchone():
            label = cedula or f"S/C ({nombre1})"
            print(f"  [SKIP] Paciente '{label}' ya existe.")
            continue

        cursor.execute(
            "INSERT INTO pacientes "
            "(cedula, nombre1, nombre2, apellido1, apellido2, "
            " lugar_nacimiento, fecha_nacimiento, estado_vital, estado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            pac,
        )
        id_paciente = cursor.lastrowid
        label = cedula or f"S/C ({nombre1})"
        print(f"  [OK] Paciente '{label}' creado (ID: {id_paciente}).")

    # Tarjetas con formato XX-XX-XX y colores auto-derivados
    tarjetas = [
        ("03-77-34", "V-12345678", None),     # Naranja
        ("15-22-80", "V-87654321", None),     # Rojo
        ("42-01-15", "V-11223344", None),     # Azul Marino
        ("08-55-02", None,         "Luis"),   # Marron (paciente sin cedula)
    ]

    for num_historia, cedula, nombre_fallback in tarjetas:
        # Buscar si la tarjeta ya existe
        cursor.execute("SELECT id FROM tarjetas WHERE num_historia = ?",
                       (num_historia,))
        if cursor.fetchone():
            print(f"  [SKIP] Tarjeta '{num_historia}' ya existe.")
            continue

        # Buscar paciente
        if cedula is not None:
            cursor.execute("SELECT id FROM pacientes WHERE cedula = ?", (cedula,))
        else:
            cursor.execute(
                "SELECT id FROM pacientes WHERE cedula IS NULL AND nombre1 = ?",
                (nombre_fallback,))
        fila_pac = cursor.fetchone()
        if not fila_pac:
            continue

        # Derivar color del ultimo par
        ultimo_par = num_historia.split("-")[2]
        decena = int(ultimo_par[0])
        nombre_color = COLORES_HOSPITAL[decena]

        cursor.execute("SELECT id FROM colores WHERE valor = ?", (nombre_color,))
        fila_color = cursor.fetchone()
        if not fila_color:
            print(f"  [WARN] Color '{nombre_color}' no encontrado. Tarjeta omitida.")
            continue

        cursor.execute(
            "INSERT INTO tarjetas (num_historia, id_paciente, id_color, estado) "
            "VALUES (?, ?, ?, 1)",
            (num_historia, fila_pac[0], fila_color[0]),
        )
        label = cedula or f"S/C ({nombre_fallback})"
        print(f"  [OK] Tarjeta '{num_historia}' -> {nombre_color} para '{label}'.")


# ── Servicios hospitalarios ───────────────────────────────────────
SERVICIOS_HOSPITAL = [
    ("Obstetricia", 20),
    ("Cirugía", 8),
    ("Medicina", 8),
    ("Pediatría", 13),
    ("Emergencia Médica", 8),
    ("Emergencia Pediátrica", 9),
]


def insertar_servicios(conn: sqlite3.Connection):
    """Inserta los 6 servicios hospitalarios con su cantidad de camas."""
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
    print("  SEED -- Datos de prueba")
    print("=" * 50)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    try:
        print("\n> Inicializando esquema...")
        inicializar_esquema(conn)

        print("\n> Insertando colores del hospital (10 colores)...")
        insertar_colores(conn)

        print("\n> Insertando usuarios...")
        insertar_usuario(conn, "Admin", "Sistema", 99999999, "admin", "admin123")
        insertar_usuario(conn, "Juan",  "Perez",   12345678, "jperez", "1234")

        print("\n> Insertando pacientes de prueba...")
        insertar_pacientes_prueba(conn)

        print("\n> Insertando servicios hospitalarios...")
        insertar_servicios(conn)

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
