# 💾 Guía 5: Capa de Acceso a Datos (DAO) — SGI Salud

Esta guía analiza el funcionamiento y diseño de la capa de **Data Access Objects (DAO)** en SGI Salud, la gestión del ciclo de vida de las conexiones a base de datos SQLite y los métodos de mapeo entre filas relacionales y objetos de software.

---

## 1. El Patrón Data Access Object (DAO)

La capa DAO actúa como un traductor y aislante. Su propósito principal es **encapsular y centralizar todo el acceso a la fuente de datos**.
* **Separación de Responsabilidades**: Los controladores y vistas no saben si los datos están almacenados en un archivo de texto, en una API web o en una base de datos SQLite. Solo interactúan con métodos del tipo `crear()`, `actualizar()` u `obtener_por_id()`.
* **Centralización de SQL**: Si mañana es necesario renombrar una columna en la base de datos o migrar de SQLite a PostgreSQL, el programador **únicamente** tendrá que modificar las consultas en los archivos de la carpeta `src/dao/`, sin tocar una sola línea de código gráfico o lógico.

---

## 2. Gestión de Conexión y Ciclo de Vida de SQLite

La conexión con la base de datos se administra mediante el módulo [conexion.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/dao/conexion.py):

```python
import sqlite3 as db

class ConexionDB:
    def __init__(self, db_path="database/database.db"):
        self.db_path = db_path

    def obtener_conexion(self):
        return db.connect(self.db_path)
```

### La Decisión de Diseño: Conexiones Abiertas/Cerradas por Operación
A diferencia de otras aplicaciones de escritorio que abren una única conexión global al arrancar y la cierran al salir, **SGI Salud abre una conexión nueva en cada método del DAO y la cierra inmediatamente al finalizar la consulta** (mediante bloques `try/finally` o cierre inmediato en retorno).

#### ¿Por qué?
1. **Evitar Bloqueos de Escritura (Locking)**: SQLite bloquea todo el archivo `.db` durante las escrituras. Si mantenemos una conexión permanente abierta escribiendo activamente, podríamos bloquear lecturas concurrentes o lanzar excepciones del tipo `database is locked`.
2. **Prevención de Corrupción de Datos**: Si la aplicación se cierra de forma inesperada (por corte de luz, apagado forzoso o error del sistema), una conexión persistente abierta podría corromper el archivo `.db`. Al abrir y cerrar rápidamente por operación, garantizamos que las transacciones sean cortas y seguras.
3. **Liberación de Memoria**: SQLite libera los buffers de memoria del sistema operativo asociados a la consulta al cerrar la conexión.

---

## 3. Anatomía de los Métodos del DAO

Los métodos de los DAOs se clasifican según su interacción con el estado de la base de datos.

### 3.1 Consultas de Lectura (Mapping Row Factory)
Para consultas de lectura (ej. `obtener_todos()`, `buscar_por_cedula()`), configuramos `row_factory = sqlite3.Row`.

```python
def obtener_todos(self) -> list[Color]:
    conn = self.db.obtener_conexion()
    conn.row_factory = sqlite3.Row  # <-- Configuración Clave
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM colores WHERE estado = 1")
    filas = cursor.fetchall()
    conn.close()
    return [Color(**dict(fila)) for fila in filas]
```

* **¿Por qué `sqlite3.Row`?** Por defecto, SQLite devuelve las filas como tuplas planas de valores ordenados `(1, "Naranja", 1)`. Esto obliga al código a recordar que el índice `0` es el ID y el `1` es el nombre. Al usar `Row`, SQLite indexa las columnas por sus nombres en la consulta SQL (como un diccionario).
* **Mapeo a Pydantic**: Convertimos la fila a un diccionario nativo de Python con `dict(fila)` y lo desempaquetamos `**` directamente dentro del constructor del modelo `Color(**dict(fila))`.

### 3.2 Consultas de Escritura (Transacciones y Commits)
Para insertar o actualizar datos (ej: `crear()`, `actualizar()`), abrimos bloques protegidos con `try/finally` para asegurar que la base de datos siempre libere sus conexiones, confirmando los cambios explícitamente con `conn.commit()`.

```python
def crear(self, color: ColorBase) -> int:
    conn = self.db.obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO colores (valor, estado) VALUES (?, 1)",
            (color.valor,),
        )
        conn.commit()  # <-- Confirmación física en el disco duro
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return -1  # Retorna código de error controlado si viola una clave única
    finally:
        conn.close()  # <-- Garantiza el cierre incluso si falla la inserción
```

* **Parametrización con `?`**: Nunca concatenamos variables directamente en strings SQL (por ejemplo, `f"INSERT ... VALUES ({color.valor})"`). Eso dejaría el sistema vulnerable a **Inyecciones SQL**. Usar `?` delega la sanitización y escape de caracteres directamente en el motor SQLite.
* **Manejo de Errores**: Si ocurre un fallo por restricción de unicidad, el bloque `except sqlite3.IntegrityError` atrapa la excepción y retorna `-1` en lugar de congelar o tumbar la aplicación, permitiendo al controlador informar elegantemente al usuario.
