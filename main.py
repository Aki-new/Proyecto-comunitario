import sqlite3
import os
import time
import pydantic

db_path = "database/database.db"
sql_path = "schema.sql"

def inicializar_db():
    # Asegurar que el directorio de datos existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Leer y ejecutar el esquema desde el archivo init.sql
    if os.path.exists(sql_path):
        with open(sql_path, 'r') as f:
            cursor.executescript(f.read())
        print("Esquema cargado exitosamente.")
    
    conn.close()

if __name__ == "__main__":
    inicializar_db()

while True:
    print("hola mundo")
    time.sleep(5)