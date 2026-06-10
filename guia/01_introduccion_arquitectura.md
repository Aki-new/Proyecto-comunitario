# 🏛️ Guía 1: Introducción y Arquitectura General — SGI Salud

Esta guía proporciona una visión integral sobre el diseño arquitectónico de **SGI Salud**, explicando cómo interactúan sus diferentes capas, la estructura del proyecto y los principios generales para comprender y modificar el sistema de forma segura.

---

## 1. Visión General del Sistema

SGI Salud es una aplicación de escritorio moderna diseñada para la gestión estadística de registros médicos (historias clínicas) en entornos hospitalarios. Su principal responsabilidad es garantizar la integridad en el registro de pacientes, la asignación automática y secuencial de identificadores de historia clínica, y la clasificación visual (por colores) de las tarjetas índice.

---

## 2. Patrón de Arquitectura: Capas Desacopladas (MVC Adaptado)

La aplicación sigue una arquitectura en capas basada en una variante del patrón **Model-View-Controller (MVC)**, complementada con el patrón **DAO (Data Access Object)** y validación declarativa mediante **Pydantic**. 

Esta separación de responsabilidades garantiza que cada archivo tenga una única misión, facilitando el mantenimiento y evitando los comunes problemas de código "espagueti" en aplicaciones de escritorio.

Las 4 capas principales son:

```
┌────────────────────────────────────────────────────────┐
│               CAPA 4: VISTA (CustomTkinter)            │  <-- Entrada de datos e interacción del usuario
└──────────────────────────┬─────────────────────────────┘
                           │ Llama métodos con dicts
                           ▼
┌────────────────────────────────────────────────────────┐
│         CAPA 3: CONTROLADOR (Lógica de Negocio)        │  <-- Orquesta flujos, valida y maneja respuestas
└──────────────────────────┬─────────────────────────────┘
                           │ Valida entrada / Ejecuta CRUD
                           ▼
┌────────────────────────────────────────────────────────┐
│            CAPA 2: DAO (Acceso a Datos SQL)            │  <-- Construye y ejecuta sentencias SQL
└──────────────────────────┬─────────────────────────────┘
                           │ Lee / Escribe
                           ▼
┌────────────────────────────────────────────────────────┐
│            CAPA 1: MODELO (Pydantic / SQLite)          │  <-- Esquema relacional y validaciones estrictas
└────────────────────────────────────────────────────────┘
```

### Detalle de Responsabilidades por Capa:

1. **Capa 1: Modelos (`src/models/`)**
   * **Misión**: Definir la estructura y restricciones del dato.
   * **Tecnología**: `Pydantic` para validaciones en caliente, tipos de datos e inicialización; archivos `.py` para lógica pura de negocio (como `num_historia_utils.py`).
   * **Regla**: No saben nada de la base de datos ni de la interfaz gráfica. Son objetos de datos puros.

2. **Capa 2: DAO - Data Access Objects (`src/dao/`)**
   * **Misión**: Centralizar las consultas SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) hacia la base de datos SQLite.
   * **Tecnología**: `sqlite3` estándar de Python.
   * **Regla**: Solo leen y escriben datos en la base de datos. Reciben modelos o parámetros simples y retornan modelos estructurados (como `TarjetaSalida` o `Paciente`). No toman decisiones de negocio (por ejemplo, no deciden qué color asignar, solo guardan el ID de color que se les da).

3. **Capa 3: Controladores (`src/controllers/`)**
   * **Misión**: Servir como cerebro orquestador de la aplicación.
   * **Responsabilidades**:
     * Recibir diccionarios crudos desde la Vista.
     * Validar dichos datos instanciando los modelos de Pydantic.
     * Coordinar con múltiples DAOs de forma secuencial (por ejemplo, crear primero un paciente y luego asociarle una tarjeta).
     * Capturar excepciones (`ValidationError`, `sqlite3.IntegrityError`) y traducirlas a tuplas legibles para la interfaz: `(exito: bool, mensaje: str)`.
   * **Regla**: No contienen código gráfico ni tocan directamente consultas SQL.

4. **Capa 4: Vistas (`src/views/`)**
   * **Misión**: Presentar la interfaz visual y capturar eventos de usuario.
   * **Tecnología**: `CustomTkinter` (Tkinter con estilos oscuros y componentes modernos).
   * **Regla**: No contienen validaciones complejas de negocio ni lógica de persistencia. Toda acción gráfica delega en un controlador, y su única responsabilidad es reaccionar al resultado `(exito, mensaje)`.

---

## 3. Estructura de Carpetas

A continuación se detalla la estructura física del código del proyecto para ubicar rápidamente cada módulo:

```
ProyectoComunitario/
├── main.py                    # Punto de entrada de la aplicación. Configura entorno y ventanas.
├── seed.py                    # Script independiente para poblar la base de datos con datos de prueba.
├── requirements.txt           # Definición de dependencias de terceros (CustomTkinter, Pydantic).
│
├── database/                  # Datos persistentes y estructura SQL.
│   ├── schema.sql             # Script SQL de creación de tablas, índices y vistas.
│   └── database.db            # Archivo de base de datos SQLite (se genera en frío al arrancar).
│
└── src/                       # Código fuente encapsulado.
    ├── models/                # Capa 1: Estructuras y reglas de validación en Python.
    │   ├── paciente.py        # Validaciones de cédula, nombres y fechas (PacienteCreate/Paciente).
    │   ├── tarjeta.py         # Validación del formato de número de historia.
    │   ├── color.py           # Datos de colores en base de datos.
    │   ├── usuario.py         # Datos de operadores.
    │   ├── busqueda.py        # Modelo de salida de la consulta unificada paciente-tarjeta.
    │   ├── config.py          # Configuración del sistema (temas, fuentes, etc.) persistida en JSON.
    │   ├── tema.py            # Diccionarios CSS/Tkinter de colores y tamaños de fuente.
    │   └── num_historia_utils.py # ALGORITMO: Asociación de rango de número a colores.
    │
    ├── dao/                   # Capa 2: Consultas SQL parametrizadas para evitar inyección SQL.
    │   ├── conexion.py        # Administrador del ciclo de vida de la conexión SQLite.
    │   ├── paciente.py        # CRUD e inserción segura de pacientes (conversión de "S/C" a NULL).
    │   ├── tarjeta.py         # CRUD de tarjetas e incremento secuencial del último número.
    │   ├── color.py           # Lectura y filtrado de colores disponibles.
    │   ├── usuario.py         # CRUD de operadores + ALGORITMO de hash SHA-256 para contraseñas.
    │   └── busqueda.py        # ALGORITMO: Motor de búsqueda inteligente multi-palabra sobre vistas SQL.
    │
    ├── controllers/           # Capa 3: Orquestadores de flujos y capturadores de errores.
    │   ├── auth_controller.py      # Control de sesión del operador activo (Login/Logout).
    │   ├── paciente_controller.py  # ALGORITMO: Transacción atómica de creación conjunta Paciente+Tarjeta.
    │   ├── tarjeta_controller.py   # Control de tarjetas y ALGORITMO de autogeneración secuencial.
    │   ├── busqueda_controller.py  # Ruteador de criterios de búsqueda.
    │   ├── color_controller.py     # Cache y catálogo de referencia visual de colores.
    │   └── usuario_controller.py   # Registro y edición de operarios.
    │
    └── views/                 # Capa 4: Pantallas, eventos e interfaz gráfica de usuario.
        ├── login_view.py      # Interfaz de acceso al sistema con validación interactiva.
        ├── dashboard_view.py  # Contenedor principal con panel de navegación lateral.
        ├── pacientes_view.py  # Módulo principal: Búsqueda dinámica y CRUD lateral comprimible.
        ├── colores_view.py    # Muestrario de los rangos de tarjetas físicas.
        ├── usuarios_view.py   # Panel de control administrativo para usuarios.
        ├── calendario_widget.py # Widget gráfico selector de fechas interactivo.
        └── selector_color_widget.py # Widget para configurar colores de tema personalizado.
```

---

## 4. Guía Práctica de Modificación: ¿Cómo extiendo el sistema?

### Escenario A: "Quiero agregar un campo a los pacientes (ej: 'telefono')"

Para añadir de forma limpia un nuevo atributo al paciente, debes seguir este orden ascendente:

1. **Base de Datos**: 
   * Modifica `database/schema.sql` agregando `"telefono" TEXT` a la tabla `pacientes`.
   * Ejecuta el script o agrégalo manualmente en `database/database.db` usando SQLite Browser.
   * Actualiza la vista `vista_paciente_tarjeta` en `schema.sql` agregando `pacientes.telefono` si deseas que aparezca en los resultados de búsqueda.
2. **Modelo**: 
   * Abre [paciente.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/paciente.py).
   * Añade `telefono: str | None = None` a `PacienteBase`. Agrega validaciones con Pydantic si es requerido (ej: regex de números telefónicos).
   * Si lo agregaste en la vista de búsqueda, añádelo en `TarjetaSalida` dentro de [busqueda.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/busqueda.py).
3. **DAO**: 
   * Modifica `src/dao/paciente.py`. Agrega el parámetro `paciente.telefono` en los métodos `crear()` y `actualizar()`.
4. **Vista**: 
   * En [pacientes_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/pacientes_view.py), añade un label y un input (`CTkEntry`) en el formulario lateral para capturar el teléfono.
   * Pásalo en el diccionario de datos hacia el controlador en el método de guardado.

---

### Escenario B: "Quiero agregar un nuevo módulo completo (ej: 'Citas Médicas')"

Si deseas implementar un módulo totalmente nuevo:

1. **Base de Datos**: Diseña la tabla en `database/schema.sql` (ej: `citas` con referencias a `pacientes`).
2. **Modelo**: Crea `src/models/cita.py` para validar fechas de cita y campos requeridos con Pydantic.
3. **DAO**: Crea `src/dao/cita.py` para insertar, editar y listar citas.
4. **Controlador**: Crea `src/controllers/cita_controller.py` para manejar la lógica (por ejemplo, evitar que se solapen dos citas a la misma hora).
5. **Vista**: 
   * Crea `src/views/citas_view.py` como un frame de CustomTkinter.
   * Agrégalo en [dashboard_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/dashboard_view.py) creando un nuevo botón en el menú lateral y enlazando la visualización del módulo de citas.
