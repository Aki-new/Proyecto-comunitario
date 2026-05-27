# 📋 Guía 3: Capa de Modelos y Estandarización de Datos — SGI Salud

Esta guía detalla la capa de **Modelos** de SGI Salud, analizando cómo se implementa la validación estrictamente declarativa y la normalización de datos en caliente a través de **Pydantic**, la persistencia de configuraciones de usuario y la gestión del sistema de temas visuales dinámicos.

---

## 1. El Rol de Pydantic en SGI Salud

En lugar de utilizar validaciones manuales condicionales (`if/else`) dispersas en toda la aplicación, SGI Salud implementa **Pydantic** (`v2.13`). Pydantic nos provee:
1. **Validación Estricta de Tipos**: Garantiza que un ID sea entero, que la cédula sea string, etc.
2. **Coerción de Datos**: Transforma los datos de entrada automáticamente a un formato estándar (por ejemplo, remueve espacios en blanco iniciales/finales, capitaliza prefijos de cédula).
3. **Mapeo de Atributos**: Facilita la conversión de diccionarios SQLite crudos a objetos limpios de Python mediante `from_attributes = True`.

---

## 2. Patrón de Herencia de Modelos

Para evitar duplicación de código entre la creación de registros (donde aún no se tiene un ID porque la base de datos no lo ha autogenerado) y la lectura de registros existentes, se aplica un patrón de herencia de tres niveles:

```
   ┌──────────────────────────────────────────────────────────┐
   │                       BaseModel                          │ (Pydantic nativo)
   └──────────────────────────┬───────────────────────────────┘
                              ▼
   ┌──────────────────────────────────────────────────────────┐
   │            Modelo Base (ej: PacienteBase)                │ (Declara todos los campos y validadores)
   └─────────────┬──────────────────────────────┬─────────────┘
                 ▼                              ▼
   ┌──────────────────────────┐   ┌───────────────────────────┐
   │  Modelo de Creación      │   │  Modelo de Lectura        │
   │   (ej: PacienteCreate)   │   │      (ej: Paciente)       │
   │  (No requiere ID en init)│   │   (Agrega id: int oblig.) │
   └──────────────────────────┘   └───────────────────────────┘
```

Por ejemplo, en [usuario.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/usuario.py):
* `UsuarioBase` declara `nombre`, `apellido`, `cedula`, `usuario` y `estado`.
* `UsuarioCreate` hereda de `UsuarioBase` y agrega el atributo `clave` (necesario solo en la creación del usuario para hashear).
* `Usuario` hereda de `UsuarioBase` y añade `id: int` (usado para cargar los operarios desde la base de datos).

---

## 3. Algoritmos de Validación y Normalización de Campos

Los validadores se definen mediante el decorador `@field_validator` de Pydantic. Analicemos cómo procesan y limpian la información en caliente antes de persistirla.

### 3.1 Validación y Normalización de la Cédula (Paciente)
El validador de cédula en [paciente.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/paciente.py) implementa un algoritmo de limpieza y formateo:

```python
@field_validator("cedula")
@classmethod
def validar_cedula(cls, v: str) -> str:
    v = v.strip()
    if not v or v.upper() == "S/C":
        return "S/C"

    # Normalizar: primera letra a mayúscula (v-123 -> V-123)
    v = v[0].upper() + v[1:]

    if not PATRON_CEDULA.match(v):
        raise ValueError(
            "Formato de cedula invalido. Use V-12345678 o E-12345678."
        )
    return v
```

* **Flujo**:
  1. Limpia espacios residuales con `.strip()`.
  2. Si es una cédula vacía o el string `"S/C"`, la estandariza como `"S/C"`.
  3. Convierte la primera letra a mayúsculas (ej: `"v-25412..."` se convierte en `"V-25412..."`).
  4. Compara contra la expresión regular `r"^[VvEe]-\d{6,10}$"`. Si no coincide (por ejemplo, omitieron el guion), lanza un error descriptivo.

### 3.2 Validación Lógica de Fechas
El validador de `fecha_nacimiento` no solo comprueba el formato visual con regex, sino que evalúa la coherencia del calendario gregoriano:

```python
@field_validator("fecha_nacimiento")
@classmethod
def validar_fecha(cls, v: str) -> str:
    v = v.strip()
    if not PATRON_FECHA.match(v):
        raise ValueError("Formato de fecha invalido. Use DD/MM/YYYY o DD-MM-YYYY.")

    # Normaliza separador guion (-) a barra diagonal (/)
    v = v.replace("-", "/")

    partes = v.split("/")
    dia, mes, anio = int(partes[0]), int(partes[1]), int(partes[2])

    if mes < 1 or mes > 12:
        raise ValueError("Mes invalido (debe ser 01-12).")
    if dia < 1 or dia > 31:
        raise ValueError("Dia invalido (debe ser 01-31).")
    if anio < 1900 or anio > 2100:
        raise ValueError("Anio invalido (debe ser 1900-2100).")

    return v
```

* **Flujo**:
  1. Captura fechas con guiones y las convierte a barras diagonales (`21-02-2000` → `21/02/2000`).
  2. Descompone el string e interpreta numéricamente Día, Mes y Año.
  3. Previene fechas imposibles (como mes 13, día 45 o años fuera de un rango humano razonable como 1820 o 2500).

---

## 4. Persistencia de Configuración del Sistema (`config.py`)

La configuración global de preferencias del operario (como la fuente y el tema visual) no se guarda en base de datos para no sobrecargar las conexiones SQLite. En su lugar, se delega al modelo [config.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/config.py), que persiste en disco como un archivo JSON plano en `database/config.json`.

* **Modelo `AppConfig`**:
  * `tema`: `str` ("oscuro", "claro", "personalizado").
  * `tamano_fuente`: `str` ("pequeno", "normal", "grande", "muy_grande").
  * `modo_num_historia`: `str` ("manual", "auto").
  * `colores_personalizados`: Objeto hijo `ColoresPersonalizados` con los códigos Hex de cada panel.
* **Ciclo de Persistencia**:
  * Al iniciar, la aplicación llama a `cargar_config()`. Si el archivo JSON no existe en la carpeta `database`, Pydantic genera uno por defecto inmediatamente con `guardar_config()`.
  * Si el operario cambia el tema en la pantalla de ajustes, la aplicación modifica el objeto `AppConfig` en memoria y llama a `guardar_config(config)` para volcarlo instantáneamente en el archivo JSON.

---

## 5. Arquitectura del Tema Dinámico (`tema.py`)

La aplicación no utiliza estilos fijos "hardcodeados" en las vistas. Cada componente visual obtiene su paleta de colores de forma reactiva de [tema.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/tema.py).

### 5.1 Resolución de Colores
El método `obtener_tema(config: AppConfig)` evalúa el tema seleccionado:
1. Si es `"oscuro"`, retorna una copia de la estructura estática `TEMA_OSCURO`.
2. Si es `"claro"`, retorna `TEMA_CLARO`.
3. Si es `"personalizado"`, ejecuta la función `_colores_personalizados_a_tema()` que hereda dinámicamente las variables de color del JSON cargado en `config.colores_personalizados` y computa colores complementarios para bordes o estados de botones al pasar el cursor (hover).

### 5.2 Tipografía Adaptativa
Para usuarios con fatiga visual, `obtener_tamano_fuente(config: AppConfig)` devuelve tamaños de texto escalables en píxeles:

| Nivel de Escala | base (Labels, Tabla) | subtitulo | titulo (Cabeceras) |
|---|---|---|---|
| **pequeno** | 10 px | 12 px | 14 px |
| **normal** | 12 px | 14 px | 16 px |
| **grande** | 14 px | 16 px | 18 px |
| **muy_grande** | 16 px | 18 px | 20 px |

Al redimensionar la fuente en configuración, todas las vistas se actualizan dinámicamente recalculando la interfaz basándose en estos mapas de píxeles.
