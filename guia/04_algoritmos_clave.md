# 🧠 Guía 4: Algoritmos Clave y Lógica de Negocio — SGI Salud

Esta guía proporciona un desglose técnico exhaustivo de los 5 algoritmos principales que controlan la lógica de negocio de **SGI Salud**, detallando sus matemáticas, flujos lógicos, por qué fueron diseñados así y cómo modificarlos de forma segura.

---

## 1. Algoritmo de Asignación Automática de Color

### Ubicación
* Módulo: [num_historia_utils.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/num_historia_utils.py)
* Funciones: `obtener_color_por_num_historia(num_historia: str) -> dict`

### Explicación del Algoritmo
El sistema de archivo del hospital utiliza carpetas físicas con pestañas de colores en el borde superior derecho para agilizar la búsqueda en archivadores físicos. La regla de negocio indica que **el color de la carpeta depende exclusivamente de la decena del último par de dígitos** del número de historia clínica (`XX-XX-XX`).

```
Ejemplo: Historia Clínica = "03-77-34"
                           1a 2o Último Par (Decena = 3)
                             
Paso 1: Validar formato.
Paso 2: Obtener el último par usando división por guion:
        "03-77-34".split("-")[2]  -->  "34"
Paso 3: Extraer el primer dígito (la decena):
        int("34"[0])              -->  3
Paso 4: Buscar en el mapa estático:
        MAPA_COLORES[3]           -->  "Naranja", Hex "#FF8C00"
```

### Tabla de Rango de Asignación Física:
El algoritmo mapea los 10 dígitos posibles (0 al 9) de la decena del último par a los siguientes colores:

| Rango de Números | Decena Extraída | Nombre del Color | Código Hex |
|---|---|---|---|
| **00 - 09** | 0 | Marrón | `#8B4513` |
| **10 - 19** | 1 | Azul Marino | `#000080` |
| **20 - 29** | 2 | Verde | `#228B22` |
| **30 - 39** | 3 | Naranja | `#FF8C00` |
| **40 - 49** | 4 | Morado | `#800080` |
| **50 - 59** | 5 | Rosa | `#FF69B4` |
| **60 - 69** | 6 | Turquesa | `#40E0D0` |
| **70 - 79** | 7 | Amarillo | `#FFD700` |
| **80 - 89** | 8 | Rojo | `#DC143C` |
| **90 - 99** | 9 | Azul Celeste | `#87CEEB` |

### ¿Cómo modificarlo?
Si el hospital cambia de proveedor de carpetas físicas y desea reasignar los colores o sus códigos hexadecimales, simplemente edita el diccionario `MAPA_COLORES` e incluye los nuevos valores hexadecimales o nombres en el archivo [num_historia_utils.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/num_historia_utils.py#L13-L26).

---

## 2. Algoritmo de Generación Secuencial de N. de Historia con Desbordamiento

### Ubicación
* Módulo: [tarjeta_controller.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/controllers/tarjeta_controller.py)
* Método: `generar_siguiente_num_historia(self) -> str`

### Explicación del Algoritmo
Cuando la aplicación está en modo de asignación automática, debe autogenerar el número de historia de forma incremental, siguiendo la estructura de pares de dígitos `XX-XX-XX`. El incremento no es un número entero simple, sino que se comporta como un contador de 3 dígitos independientes en base 100 (valores del 00 al 99).

```
Flujo del Algoritmo:
1. Obtiene el último número de historia activo desde SQLite (ID de tarjeta más alto).
   * Si no hay registros previos, retorna la constante semilla: "00-00-01".
2. Divide el número en 3 partes numéricas:
   par1 (primero), par2 (medio), par3 (último)
3. Incrementa el último par (par3 += 1).
4. Aplica las reglas de desbordamiento secuencial en cascada:
   ┌─────────────────────────────────────────────────────────────┐
   │                       Incremento par3                       │
   └───────────────┬─────────────────────────────────────────────┘
                   │
            ¿par3 > 99? ─ NO ─► Retorna XX-XX-(par3)
                   │ SI
   ┌───────────────▼─────────────────────────────────────────────┐
   │           Reinicia par3 = 0, incrementa par2               │
   └───────────────┬─────────────────────────────────────────────┘
                   │
            ¿par2 > 99? ─ NO ─► Retorna XX-(par2)-00
                   │ SI
   ┌───────────────▼─────────────────────────────────────────────┐
   │           Reinicia par2 = 0, incrementa par1               │
   └───────────────┬─────────────────────────────────────────────┘
                   │
            ¿par1 > 99? ─ NO ─► Retorna (par1)-00-00
                   │ SI
   ┌───────────────▼─────────────────────────────────────────────┐
   │  Desbordamiento total de capacidad: Reinicia a "00-00-00"    │
   └─────────────────────────────────────────────────────────────┘
```

### Casos de Ejemplo Práctico:
* **Incremento Normal**: `'03-77-34'` → `'03-77-35'`
* **Desbordamiento Primer Nivel**: `'03-77-99'` → `'03-78-00'`
* **Desbordamiento Segundo Nivel**: `'03-99-99'` → `'04-00-00'`
* **Desbordamiento Límite Máximo**: `'99-99-99'` → `'00-00-00'` (Reinicio preventivo del sistema).

---

## 3. Algoritmo de Búsqueda Inteligente Multipalabra

### Ubicación
* Módulo: [busqueda.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/dao/busqueda.py)
* Método: `buscar_por_nombre_completo(self, texto: str) -> list[TarjetaSalida]`

### Explicación del Algoritmo
Cuando un usuario escribe `"María Pérez"` en la barra de búsqueda general, no podemos buscar de forma literal `"María Pérez"` en una columna, ya que los nombres y apellidos están divididos en 4 columnas separadas en la base de datos (`nombre1`, `nombre2`, `apellido1`, `apellido2`). 

El algoritmo descompone el string ingresado y genera dinámicamente una consulta SQL que cruza cada palabra contra todas las columnas de nombres de forma independiente.

```
Si el usuario ingresa: "Maria Gonzalez"

Paso 1: Limpia espacios redundantes y fragmenta en palabras individuales:
        palabras = ["Maria", "Gonzalez"]

Paso 2: Si está vacío, retorna obtener_todos().

Paso 3: Para CADA palabra, genera un bloque de condición WHERE:
        Condición_Palabra_1:
        (nombre1 LIKE '%Maria%' COLLATE NOCASE 
         OR COALESCE(nombre2,'') LIKE '%Maria%' COLLATE NOCASE 
         OR apellido1 LIKE '%Maria%' COLLATE NOCASE 
         OR COALESCE(apellido2,'') LIKE '%Maria%' COLLATE NOCASE)
         
        Condición_Palabra_2:
        (nombre1 LIKE '%Gonzalez%' COLLATE NOCASE 
         OR COALESCE(nombre2,'') LIKE '%Gonzalez%' COLLATE NOCASE 
         OR apellido1 LIKE '%Gonzalez%' COLLATE NOCASE 
         OR COALESCE(apellido2,'') LIKE '%Gonzalez%' COLLATE NOCASE)

Paso 4: Une las condiciones mediante el operador lógico estricto "AND":
        WHERE Condición_Palabra_1 AND Condición_Palabra_2

Paso 5: Prepara y sanitiza la lista de parámetros para evitar inyecciones SQL:
        parametros = ["%Maria%", "%Maria%", "%Maria%", "%Maria%",
                      "%Gonzalez%", "%Gonzalez%", "%Gonzalez%", "%Gonzalez%"]
```

### Decisiones de Diseño Críticas:
1. **`COALESCE(nombre2, '')`**: Si un paciente no tiene segundo nombre, su valor en base de datos es `NULL`. En SQL, cualquier comparación `LIKE NULL` da como resultado `NULL` (Falso). Utilizar `COALESCE` reemplaza el `NULL` por un texto vacío `''`, permitiendo que la búsqueda no falle.
2. **`COLLATE NOCASE`**: SQLite por defecto es sensible a mayúsculas y minúsculas en búsquedas `LIKE` cuando se usan caracteres especiales. Agregar de forma explícita `COLLATE NOCASE` fuerza al motor a ignorar la diferencia entre `"maria"`, `"MARÍA"` o `"Maria"`.

---

## 4. Algoritmo de Autenticación y Hasheo SHA-256 para Contraseñas

### Ubicación
* Módulo: [usuario.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/dao/usuario.py)
* Métodos: `_hash_clave(clave: str) -> str` y `validar_credenciales(nombre_usuario: str, clave: str)`

### Explicación del Algoritmo
Por normativas estrictas de seguridad de la información, **nunca se deben almacenar contraseñas en texto plano** en una base de datos. Si un atacante robase el archivo `.db`, obtendría los accesos de todos los operadores del sistema.

SGI Salud implementa un esquema de hash criptográfico unidireccional de nivel industrial mediante **SHA-256**:

```
Registrar Usuario:
Texto Plano: "Clave123" ─► Codificar en UTF-8 ─► Hash SHA-256 ─► Almacenar en DB: "7f4c5..." (64 caracteres Hex)

Validar Login:
1. Operario ingresa usuario "admin" y contraseña "Clave123".
2. El sistema consulta a la DB el hash almacenado para el usuario "admin".
3. Hashea la clave ingresada: hash("Clave123") --> "7f4c5..."
4. Compara ambos hashes en memoria:
   ¿hash_almacenado == hash_ingresado?
   * Si son idénticos, se concede acceso.
   * Si difieren, se rechaza la solicitud de login.
```

* **Propiedad Unidireccional**: Es computacionalmente imposible revertir el hash `"7f4c5..."` para obtener el string original `"Clave123"`.

---

## 5. Algoritmo de Traducción e Inserción de Pacientes sin Cédula ("S/C")

### Ubicación
* Módulo: [paciente.py (DAO)](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/dao/paciente.py)
* Métodos: `crear()`, `actualizar()` y `_fila_a_paciente()`

### Explicación del Algoritmo
Como se explicó en la Guía de Base de Datos, para evitar colisiones Unique y mantener la normalización relacional, los pacientes sin cédula se persisten como `NULL` en la base de datos, pero el usuario debe verlos siempre representados amigablemente como `"S/C"`. 

El DAO actúa como un middleware traductor bidireccional automático:

```
                  ┌─────────────────────────────────────┐
                  │            Escritura (Vista)        │
                  │             Paciente: "S/C"         │
                  └──────────────────┬──────────────────┘
                                     │
                    ¿Es cedula == "S/C", "" o None?
                                    / \
                              SÍ   /   \  NO
                                  /     \
                                 ▼       ▼
                           cedula=None   cedula=cedula (ej: V-12)
                                 │       │
                                 ▼       ▼
                               INSERT en SQLite
                                 │
                                 ▼
                  ┌─────────────────────────────────────┐
                  │          Lectura (Base Datos)       │
                  │           SQLite row["cedula"]      │
                  └──────────────────┬──────────────────┘
                                     │
                              ¿Es NULL en DB?
                                    / \
                              SÍ   /   \  NO
                                  /     \
                                 ▼       ▼
                            cedula="S/C" cedula=row["cedula"]
                                 │       │
                                 ▼       ▼
                  ┌─────────────────────────────────────┐
                  │            Salida (Frontend)        │
                  │             Paciente: "S/C"         │
                  └─────────────────────────────────────┘
```

Este algoritmo garantiza que el código de la interfaz gráfica no necesite validar manualmente si el dato es nulo o no, ya que siempre tratará a la cédula como una cadena de texto limpia.
