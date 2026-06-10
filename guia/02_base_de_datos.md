# 🗄️ Guía 2: Capa de Base de Datos y Persistencia — SGI Salud

Esta guía describe el funcionamiento de la base de datos de SGI Salud, analizando su motor, el diseño del esquema de tablas, el comportamiento de las restricciones relacionales, los índices de optimización y el mecanismo de borrado lógico.

---

## 1. Motor de Base de Datos: SQLite3

SGI Salud utiliza **SQLite** como motor de persistencia. Se trata de un motor relacional embebido y autónomo.
* **Ventajas**: No requiere instalar ni configurar un servidor externo (como MySQL o PostgreSQL). Todo el estado se almacena en un único archivo físico ubicado en `database/database.db`.
* **Seguridad de Acceso**: Dado que es una aplicación monousuario (de escritorio), SQLite es óptimo en velocidad de lectura y escritura concurrente, utilizando locks a nivel de base de datos durante las transacciones de escritura.

---

## 2. Esquema Relacional de Tablas

El esquema de la base de datos está estructurado en 4 tablas principales diseñadas con el fin de evitar la redundancia y garantizar la integridad referencial. El script SQL original de inicialización está en [schema.sql](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/database/schema.sql).

```
   ┌───────────┐            ┌───────────┐           ┌─────────┐
   │ pacientes │1 -------- 1│ tarjetas  │N ------- 1│ colores │
   └───────────┘            └───────────┘           └─────────┘
                                  
                            ┌───────────┐
                            │ usuarios  │
                            └───────────┘
```

### 2.1 Tabla `colores`
Contiene la lista predefinida de 10 colores asociados a las decenas de los números de historia clínica.
* **id** (INTEGER, Primary Key, Autoincrement)
* **valor** (TEXT, NOT NULL): Nombre en español (ej: "Naranja", "Morado").
* **estado** (INTEGER, NOT NULL): `1` para activo, `0` para inactivo.

### 2.2 Tabla `pacientes`
Almacena los datos filiatorios de los pacientes atendidos.
* **id** (INTEGER, Primary Key, Autoincrement)
* **cedula** (TEXT, Nullable): Cédula de identidad (ej: "V-12345678"). Se permite `NULL` para niños sin cédula (mostrados como "S/C").
* **nombre1** (TEXT, NOT NULL)
* **nombre2** (TEXT, Nullable)
* **apellido1** (TEXT, NOT NULL)
* **apellido2** (TEXT, Nullable)
* **lugar_nacimiento** (TEXT, NOT NULL)
* **fecha_nacimiento** (TEXT, NOT NULL): Almacenada en formato estandarizado `DD/MM/AAAA`.
* **estado_vital** (INTEGER, NOT NULL): `1` para Vivo, `0` para Fallecido.
* **estado** (INTEGER, NOT NULL): `1` para Activo (Vigente), `0` para Eliminado (Borrado Lógico).

### 2.3 Tabla `tarjetas`
Representa la tarjeta índice del paciente. Es la entidad puente que vincula un paciente con su número de historia clínica y color de pestaña.
* **id** (INTEGER, Primary Key, Autoincrement)
* **num_historia** (TEXT, NOT NULL, UNIQUE): El código `XX-XX-XX`.
* **id_paciente** (INTEGER, NOT NULL, Foreign Key → `pacientes(id)`): Relación estricta 1 a 1.
* **id_color** (INTEGER, NOT NULL, Foreign Key → `colores(id)`): Relación N a 1.
* **estado** (INTEGER, NOT NULL): `1` para Activa, `0` para Inactiva.

### 2.4 Tabla `usuarios`
Almacena los registros de los operarios de la aplicación.
* **id** (INTEGER, Primary Key, Autoincrement)
* **nombre** (TEXT, NOT NULL)
* **apellido** (TEXT, NOT NULL)
* **cedula** (INTEGER, NOT NULL, UNIQUE)
* **usuario** (TEXT, NOT NULL, UNIQUE): Nombre de acceso (login).
* **clave** (TEXT, NOT NULL): Hash criptográfico SHA-256 de la clave (no texto plano).
* **estado** (INTEGER): `1` para Activo, `0` para Inactivo.

---

## 3. Comportamientos Críticos de Restricciones y Reglas de Negocio

### 3.1 El problema de "Sin Cédula" (S/C) y la restricción UNIQUE
En hospitales, los recién nacidos o niños muy pequeños no poseen cédula de identidad propia. En el frontend, se les identifica como `"S/C"` (Sin Cédula).

> [!IMPORTANT]
> Si la columna `cedula` en la tabla `pacientes` tuviera la restricción `UNIQUE` y se guardara como `"S/C"`, **solo podríamos registrar a un único paciente sin cédula** en todo el sistema. 
>
> **Solución Implementada**:
> 1. En la tabla de SQLite, la columna `cedula` **no tiene** restricción UNIQUE a nivel de motor.
> 2. Permite valores `NULL`. SQLite permite múltiples valores `NULL` independientes.
> 3. En el DAO `src/dao/paciente.py`, al insertar en base de datos, si el paciente es `"S/C"`, se traduce y se guarda como `NULL` (valor vacío).
> 4. Al leer de la base de datos, el DAO traduce automáticamente cualquier `NULL` a `"S/C"` antes de enviarlo a la interfaz.
> 5. La validación de unicidad de cédulas válidas (ej: `V-12345678`) se realiza de forma inteligente en el controlador `PacienteController` consultando previamente con `obtener_por_cedula()`.

### 3.2 Relación Atómica 1:1 Paciente-Tarjeta
Cada paciente debe tener **una sola tarjeta activa**. Para evitar desbalances en el sistema físico de archivos del hospital:
* Antes de crear una tarjeta, `TarjetaDAO.paciente_tiene_tarjeta(id_paciente)` realiza una verificación rápida. Si el paciente ya posee una tarjeta activa (`estado = 1`), se aborta el registro.

---

## 4. Vista Unificada: `vista_paciente_tarjeta`

Para evitar que los DAOs o controladores tengan que realizar múltiples sentencias `JOIN` complejas en Python, se ha definido una vista relacional optimizada a nivel de motor SQLite:

```sql
CREATE VIEW IF NOT EXISTS vista_paciente_tarjeta AS
SELECT
    pacientes.id AS id_paciente,
    pacientes.nombre1,
    pacientes.nombre2,
    pacientes.apellido1,
    pacientes.apellido2,
    COALESCE(pacientes.cedula, 'S/C') AS cedula,
    pacientes.fecha_nacimiento,
    pacientes.lugar_nacimiento,
    pacientes.estado_vital,
    tarjetas.num_historia,
    colores.valor AS color
FROM pacientes
JOIN tarjetas ON pacientes.id = tarjetas.id_paciente
JOIN colores ON colores.id = tarjetas.id_color
WHERE pacientes.estado = 1;
```

### ¿Por qué es clave esta vista?
1. **Rendimiento**: SQLite compila y ejecuta esta vista en código nativo de bajo nivel, siendo órdenes de magnitud más rápido que recuperar listas por separado y cruzarlas en Python.
2. **Abstracción**: Permite al motor de búsqueda (`BusquedaDAO`) consultar contra una única estructura plana de campos (por ejemplo, `SELECT * FROM vista_paciente_tarjeta WHERE cedula LIKE ...`).
3. **Mapeo Limpio**: Usa `COALESCE(pacientes.cedula, 'S/C')`, garantizando que en consultas de lectura la interfaz siempre reciba `"S/C"` si el paciente carece de cédula en disco.

---

## 5. Índices de Rendimiento (Performance Tuning)

Conforme el volumen de pacientes crece (miles de registros), las consultas secuenciales (`Full Table Scan`) sobre campos de texto harían que la aplicación se congele. Para mitigar esto, en [schema.sql](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/database/schema.sql) se definen índices balanceados en árbol (B-Tree):

* `idx_historias_id_paciente` en la tabla `tarjetas (id_paciente)`: Acelera las búsquedas cruzadas 1:1.
* `idx_pacientes_numero_cedula` en la tabla `pacientes (cedula)`: Optimiza la validación de duplicados y búsquedas de pacientes.
* `idx_pacientes_primer_apellido` e `idx_pacientes_primer_nombre` en `pacientes (apellido1)` y `pacientes (nombre1)` respectivamente: Hacen que las búsquedas por nombre/apellido del paciente en el motor de búsqueda sean instantáneas.

---

## 6. Mecanismo de Borrado Lógico (Soft Delete)

SGI Salud sigue el principio de preservación no destructiva de datos. **Ninguna consulta de la aplicación utiliza la sentencia `DELETE`**.

### ¿Cómo funciona el Soft Delete?
1. Cada tabla posee una columna `estado` (tipo `INTEGER`, `1` = Activo, `0` = Desactivado).
2. Cuando el operario pulsa "Eliminar", se ejecuta una consulta de actualización:
   ```sql
   UPDATE pacientes SET estado = 0 WHERE id = ?
   ```
3. Todas las consultas de lectura filtran activamente:
   ```sql
   SELECT * FROM pacientes WHERE estado = 1
   ```
4. **Beneficio**: Si el operador elimina un registro por accidente, el administrador de base de datos puede restaurarlo en segundos simplemente cambiando el campo `estado` a `1` directamente en la base de datos, garantizando además que el histórico referencial (por ejemplo, números de historia asignados) no se rompa físicamente.
