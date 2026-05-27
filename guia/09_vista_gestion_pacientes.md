# 👤 Guía 9: Vista de Gestión de Pacientes y Calendario — SGI Salud

Esta guía detalla el funcionamiento interno de la pantalla central de la aplicación, **PacientesView**, y de sus componentes auxiliares interactivos en [calendario_widget.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/calendario_widget.py), analizando sus estructuras, variables, layouts adaptativos y algoritmos gráficos.

---

## 1. PacientesView — Módulo Unificado de Gestión

### Ubicación del Código
* [pacientes_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/pacientes_view.py)

### Responsabilidad
Consolidar en una sola pantalla la barra de búsquedas con debounce, el listado de pacientes en grilla, la visualización de tarjetas físicas y el formulario CRUD responsivo.

### 1.1 Constantes de Configuración de Tabla
* `CRITERIOS`: Array de tuplas `(clave, etiqueta)` que define el mapeo para el dropdown de búsqueda.
* `ANCHOS_COLUMNAS` (`[90, 180, 85, 110, 80, 100]`): Ancho fijo en píxeles asignado a cada columna del listado para asegurar alineación perfecta.
* `NOMBRES_COLUMNAS` (`["Cedula", "Nombre", "F. Nac.", "Lugar Nac.", "N. Historia", "Color"]`): Cabeceras visuales de la tabla.

### 1.2 Atributos y Variables de Instancia
* **Controladores**:
  * `controlador_paciente` (instancia de `PacienteController`)
  * `controlador_tarjeta` (instancia de `TarjetaController`)
  * `controlador_busqueda` (instancia de `BusquedaController`)
* **Estado Interno**:
  * `id_paciente_seleccionado` (`int | None`): ID del paciente cargado en el formulario (indica modo edición si tiene valor, o creación si es `None`).
  * `id_tarjeta_seleccionada` (`int | None`): ID de la tarjeta del paciente en edición.
  * `_widgets_filas_tabla` (`list[CTkFrame]`): Referencias a los marcos visuales de cada fila del listado (permite destruirlas limpiamente al recargar).
  * `_formulario_visible` (`bool`): Bandera que indica si el formulario lateral está desplegado.
  * `_id_debounce_busqueda` (`str | None`): ID de la tarea retardada programada en el event loop para la búsqueda en vivo.
* **Widgets Relevantes**:
  * `entrada_busqueda` (`CTkEntry`): Campo de búsqueda.
  * `selector_tipo_cedula` (`CTkOptionMenu`): Desplegable `"V-"`, `"E-"`, `"S/C"`.
  * `entrada_numero_cedula` (`CTkEntry`): Entrada del número de cédula.
  * `campo_fecha_nacimiento` (instancia de `CampoFecha`): Selector de fecha compuesto.
  * `modo_historia` (`CTkSegmentedButton`): Selector de modo `"Manual"` o `"Auto"`.
  * `entrada_num_historia` (`CTkEntry`): Entrada del número de historia.
  * `cuadro_color_preview` (`CTkFrame`): Cuadrado físico para la preview del color.
  * `etiqueta_nombre_color` (`CTkLabel`): Texto con el nombre de la preview de color.
  * `etiqueta_errores` (`CTkLabel`): Label inferior para pintar errores de validación de negocio.

### 1.3 Métodos Clave del Módulo

#### `_construir_interfaz(self)`
Construye la distribución de la pantalla:
1. Barra superior de búsquedas con botones.
2. Línea de estado con conteo en tiempo real (`self.etiqueta_conteo`).
3. Marco contenedor del cuerpo (`self.cuerpo`), configurando la columna `0` (tabla) como expandible.

#### `_mostrar_formulario(self, titulo)` / `_cerrar_formulario(self)`
**Algoritmo de Layout Adaptativo (Compresión Dinámica)**:
* Por defecto, la columna 0 (tabla) tiene peso 1 y la columna 1 (formulario) tiene peso 0.
* Al abrir el formulario:
  * Cambia pesos: columna 0 peso 55, columna 1 peso 45.
  * Instancia el panel del formulario en la columna 1: `.grid(row=0, column=1, sticky="nsew", padx=(6,0))`.
* Al cerrar:
  * Restablece pesos: columna 0 peso 1, columna 1 peso 0.
  * Oculta el formulario (`self.panel_formulario.grid_forget()`), expandiendo la tabla al 100%.

#### `_al_cambiar_tipo_cedula(self, valor)`
Habilita o deshabilita en caliente el campo de escritura de cédula. Si selecciona `"S/C"`, vacía y deshabilita la entrada; de lo contrario, la activa.

#### `_obtener_cedula_completa(self)` / `_establecer_cedula(self, cedula)`
* **Lectura**: Si el dropdown está en `"S/C"`, retorna `"S/C"`. De lo contrario, concatena el tipo (V-/E-) con el valor del input.
* **Escritura**: Parsea strings como `"E-22501..."` y posiciona el selector en `"E-"` e inyecta `"22501..."` en el entry numérico.

#### `_al_cambiar_modo_historia(self, valor)`
Si el modo se cambia a `"Auto"`, consulta al controlador de tarjetas el siguiente número secuencial de historia clínica (`generar_siguiente_num_historia()`) y lo auto-escribe en el campo de texto, bloqueando la edición manual.

#### `_busqueda_en_vivo(self)`
**Algoritmo de Debounce (Filtro Anti-rebote)**:
Para evitar sobrecargar de consultas SQLite la base de datos al tipear caracteres en la barra de búsqueda rápida:
```python
if self._id_debounce_busqueda:
    self.after_cancel(self._id_debounce_busqueda)
self._id_debounce_busqueda = self.after(300, self._ejecutar_busqueda)
```
* **Funcionamiento**: Cancela cualquier consulta programada previamente y agenda una nueva a los 300ms. La consulta real solo se dispara cuando el operario detiene su escritura por al menos 0.3 segundos.

#### `_renderizar_resultados(self, registros)`
Limpia la grilla y dibuja las filas de datos.
* **Preview visual**: Lee el número de historia de cada registro, calcula su color y pinta un indicador circular (`indicador_color`) con el color real de la tarjeta al lado de su nombre, facilitando la visualización espacial.
* **Event Binding**: Vincula el clic de cada celda y de la fila al método de selección.

#### `_seleccionar_paciente(self, registro)`
Carga los datos del paciente y su tarjeta en el formulario lateral, cambiando el título del panel a `"Editar Registro"` y abriendo el formulario lateral de forma dinámica.

#### `_guardar_paciente(self)`
Recopila los datos del formulario, los valida localmente y decide qué controlador llamar:
* Si `id_paciente_seleccionado` es `None`, llama a `registrar_paciente_con_tarjeta()`.
* Si está en modo edición, llama a `actualizar_paciente()` y seguidamente a `actualizar_tarjeta()`.
* Tras la transacción, refresca la grilla y cierra el formulario lateral.

---

## 2. Calendario Reutilizable — [calendario_widget.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/calendario_widget.py)

El módulo define dos clases desacopladas para la captura de fechas válidas: **CampoFecha** (input + botón) y **CalendarioPopup** (ventana emergente de cuadrícula gregoriana).

### 2.1 CampoFecha (Widget Compuesto)
Hereda de `ctk.CTkFrame`.
* **Atributos**:
  * `entrada_fecha` (`CTkEntry`): Input directo para tipear fechas manuales (`DD/MM/AAAA`).
  * `boton_calendario` (`CTkButton`): Botón interactivo con ícono 📅.
  * `_popup_abierto` (`bool`): Semáforo para prevenir que el usuario abra múltiples ventanas de calendario si hace doble clic sobre el botón.
* **Métodos Públicos**:
  * `obtener_fecha() -> str`: Devuelve el string escrito o seleccionado.
  * `establecer_fecha(fecha: str)`: Escribe una fecha en el input.
  * `_abrir_calendario()`: Si `_popup_abierto` es `False`, instancia la clase `CalendarioPopup` posicionándola justo debajo del botón.

---

### 2.2 CalendarioPopup (Ventana Emergente Gregoriana)
Hereda de `ctk.CTkToplevel` (ventana sin marcos nativos del sistema operativo).

* **Atributos de Calendario**:
  * `_anio_actual`, `_mes_actual`: Período del mes renderizado.
  * `_dia_hoy` (`datetime.date`): Fecha actual del reloj del sistema.
  * `marco_grilla_dias` (`CTkFrame`): Contenedor de los botones de los días.
  * `etiqueta_mes_anio` (`CTkLabel`): Rótulo central que informa el mes y año (ej: "Marzo 2026").

#### Métodos y Algoritmos Críticos:

#### `__init__(self, parent, callback, tema=None, fuente_tamano=None)`
* Elimina los bordes del sistema operativo ejecutando `self.wm_overrideredirect(True)`.
* Bloquea la interacción modal con `self.grab_set()`.
* Construye el encabezado de navegación y la cuadrícula.
* Se auto-posiciona en pantalla mediante `_posicionar_popup(parent)`.
* Vincula la pérdida de foco (`<FocusOut>`) al autocierre preventivo.

#### `_renderizar_mes(self)` (ALGORITMO CLAVE)
Dibuja dinámicamente el mes actual utilizando la biblioteca `calendar` de Python:
1. Obtiene las semanas del mes: `calendar.Calendar(0).monthdayscalendar(anio, mes)` (ej: una matriz de 7 columnas).
2. **Tratamiento de Días Huérfanos**:
   * Si la primera semana empieza en jueves, las columnas de Lunes a Miércoles devuelven valor `0` (días huérfanos).
   * El algoritmo calcula el último día del mes anterior y rellena estas celdas vacías pintando los números correspondientes con letra gris tenue (`COLOR_TEXT_SEC`), haciendo que el calendario sea continuo.
   * Lo mismo realiza al final de la última semana, rellenando con los primeros días del mes siguiente (`1`, `2`, `3`).
3. **Resaltado de Hoy**: Compara cada celda contra `_dia_hoy`. Si coincide, le asigna el color de acento (`COLOR_ACCENT`) y letra blanca en negrita, destacando la fecha actual.
4. Vincula el clic del botón del día a `_seleccionar_dia()`.

#### `_posicionar_popup(self, widget_padre)` (ALGORITMO DE POSICIONAMIENTO)
Calcula las coordenadas de pantalla para abrir la ventana flotante pegada al botón de calendario:
* Obtiene las coordenadas absolutas en pantalla del botón mediante `widget_padre.winfo_rootx()` y `widget_padre.winfo_rooty()`.
* **Ajuste de Bordes (Screen boundary check)**:
  * Si el popup excede el ancho derecho de la pantalla, lo desplaza a la izquierda: `pos_x = ancho_pantalla - ancho_popup - 8`.
  * Si excede la altura inferior, lo despliega **arriba** del botón en lugar de abajo: `pos_y = y_padre - alto_popup - 4`.
* Aplica las coordenadas definitivas con `self.geometry(f"+{pos_x}+{pos_y}")`.
