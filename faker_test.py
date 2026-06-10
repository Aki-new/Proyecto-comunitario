import sqlite3
import random
import faker
from datetime import datetime

fake = faker.Faker()
DB_NAME = 'database\database.db' # Coloca la ruta real de tu archivo .db

def poblar_sistema_medico():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    
    # Optimizaciones de velocidad para SQLite
    cursor.execute("PRAGMA journal_mode = MEMORY;")
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA cache_size = -100000;")
    cursor.execute("PRAGMA foreign_keys = OFF;") # Desactivar temporalmente para máxima velocidad
    
    # Asegurar que exista al menos un color de prueba con ID 1
    cursor.execute("INSERT OR IGNORE INTO colores (id, valor, estado) VALUES (1, 'Color de Prueba', 1);")
    conexion.commit()
    
    # Averiguar en qué ID comenzar por si ya tienes datos previos
    cursor.execute("SELECT MAX(id) FROM pacientes;")
    ultimo_id = cursor.fetchone()[0]
    id_actual = (ultimo_id if ultimo_id is not None else 0) + 1
    
    total_registros = 1000000
    tamano_lote = 25000 # Reducimos un poco el lote porque insertaremos en dos tablas a la vez
    
    print(f"Iniciando inyección de {total_registros} pacientes con sus respectivas tarjetas...")
    inicio_total = datetime.now()
    
    for lote_idx in range(0, total_registros, tamano_lote):
        cursor.execute("BEGIN TRANSACTION;")
        
        lista_pacientes = []
        lista_tarjetas = []
        
        for _ in range(tamano_lote):
            cedula = f"{random.choice(['V', 'E'])}-{id_actual:08d}"
            num_historia = f"{random.randint(10,99)}-{random.randint(10,99)}-{id_actual}" # Garantiza historia única
            
            # Datos alineados estrictamente a tus columnas de 'pacientes'
            # (id, nombre1, nombre2, apellido1, apellido2, cedula, lugar_nacimiento, fecha_nacimiento, estado_vital, estado)
            paciente = (
                id_actual,
                fake.first_name(),
                fake.first_name(),
                fake.last_name(),
                fake.last_name(),
                cedula,
                fake.city(),
                fake.date_of_birth(minimum_age=11, maximum_age=100).strftime("%d-%m-%Y"),
                random.choice([0, 1]),
                1 # Estado activo
            )
            lista_pacientes.append(paciente)
            
            # Datos alineados estrictamente a tus columnas de 'tarjetas'
            # (num_historia, id_paciente, id_color, estado)
            tarjeta = (
                num_historia,
                id_actual,
                1, # ID del color creado al inicio
                1  # Estado activa
            )
            lista_tarjetas.append(tarjeta)
            
            id_actual += 1
            
        # Inserción masiva en tabla Pacientes (forzando el ID manual para sincronizar)
        cursor.executemany("""
            INSERT INTO pacientes (id, nombre1, nombre2, apellido1, apellido2, cedula, lugar_nacimiento, fecha_nacimiento, estado_vital, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, lista_pacientes)
        
        # Inserción masiva correspondiente en tabla Tarjetas
        cursor.executemany("""
            INSERT INTO tarjetas (num_historia, id_paciente, id_color, estado)
            VALUES (?, ?, ?, ?);
        """, lista_tarjetas)
        
        conexion.commit()
        print(f"-> Procesados {id_actual - 1} registros totales...")
        
    # Reactivar llaves foráneas y cerrar
    cursor.execute("PRAGMA foreign_keys = ON;")
    conexion.close()
    print(f"¡Éxito absoluto! Sistema poblado en: {datetime.now() - inicio_total}")

def sincronizar_fts():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    print("Sincronizando pacientes existentes hacia FTS5...")
    # Limpiamos e insertamos todo de nuevo
    cursor.execute("DELETE FROM pacientes_fts;")
    cursor.execute("""
        INSERT INTO pacientes_fts(rowid, id_paciente, nombres, apellidos, cedula)
        SELECT id, id, nombre1 || ' ' || COALESCE(nombre2, ''), apellido1 || ' ' || COALESCE(apellido2, ''), cedula
        FROM pacientes;
    """)
    conexion.commit()
    conexion.close()
    print("¡Sincronización FTS5 completa!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        sincronizar_fts()
    else:
        poblar_sistema_medico()
        # Sincronizamos por si acaso, aunque los triggers deberían hacerlo
        sincronizar_fts()
