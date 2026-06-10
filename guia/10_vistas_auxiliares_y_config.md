# ⚙️ Guía 10: Detalle de Vistas de Configuración y Auxiliares — SGI Salud

Esta guía detalla el funcionamiento interno de las pantallas secundarias y de soporte del sistema: **ConfiguracionView** (ajustes visuales y picker de temas), **SelectorColorPopup** (selector visual de colores), **ColoresView** (catálogo de colores de historias) y **UsuariosView** (CRUD de operadores y cambio de claves).

---

## 1. ConfiguracionView — Panel de Ajustes del Sistema

### Ubicación del Código
* [configuracion_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/configuracion_view.py)

### Responsabilidad
Permitir la personalización del entorno visual (Temas Oscuro/Claro/Personalizado), escalar la tipografía general, y configurar el modo de asignación de números de historia clínica (Manual o Automático).

### 1.1 Atributos e Indexadores de Estado
* **Mapas de Conversión Inversa**: Traducen las etiquetas amigables del español de CustomTkinter a claves crudas de datos:
  * `_MAPA_TEMAS` / `_MAPA_TEMAS_INV`: `"Oscuro"` ↔ `"oscuro"`, `"Claro"` ↔ `"claro"`, `"Personalizado"` ↔ `"personalizado"`.
  * `_MAPA_TAMANOS` / `_MAPA_TAMANOS_INV`: `"Normal"` ↔ `"normal"`, `"Grande"` ↔ `"grande"`, etc.
  * `_MAPA_MODO` / `_MAPA_MODO_INV`: `"Automático"` ↔ `"auto"`, `"Manual"` ↔ `"manual"`.
* **Configuración del Color Personalizado**:
  * `_CAMPOS_COLOR`: Array que vincula el atributo del modelo con su etiqueta visual:
    `[("fondo", "Fondo"), ("panel", "Panel"), ("acento", "Acento"), ...]`
  * `_entradas_color` (`dict[str, CTkEntry]`): Almacena las cajas de texto de los códigos Hexadecimales de cada color personalizado.
  * `_previews_color` (`dict[str, CTkFrame]`): Mapea los marcos de visualización de colores en el formulario.
* **Controladores e Interfaces**:
  * `on_config_changed` (`callable`): Callback que invoca `aplicar_tema()` en `DashboardView` al guardar los cambios en disco.
  * `selector_tema` (`CTkSegmentedButton`): Selector de tema.
  * `selector_tamano` (`CTkSegmentedButton`): Selector de tamaño de fuente.
  * `label_preview_fuente` (`CTkLabel`): Zona de texto dinámico para previsualizar el tamaño antes de confirmar.

### 1.2 Métodos del Módulo

#### `_crear_fila_color(self, parent, campo, etiqueta, valor_inicial)`
**Algoritmo de Fila de Color Picker**:
* Para cada uno de los 6 atributos de color personalizado, dibuja una fila compuesta:
  1. Label descriptivo.
  2. Caja de texto (`CTkEntry`) con el código Hex.
  3. Cuadro gráfico (`CTkFrame`) relleno con el color real.
* **Comportamiento**:
  * Vincula `<KeyRelease>` en el entry para que al escribir el código (ej: `#FFFFFF`), ejecute `_actualizar_preview()` y redibuje el color del cuadro gráfico instantáneamente.
  * Vincula el clic del ratón `<Button-1>` sobre el cuadro gráfico para abrir el picker visual `SelectorColorPopup`.

#### `_abrir_color_picker(self, campo)`
Instancia la ventana flotante `SelectorColorPopup` pasándole como coordenada de anclaje el propio cuadro de preview clicado y configurando un callback que escribirá el color seleccionado.

#### `_actualizar_preview(self, campo)`
**Algoritmo de Validación de Expresión Regular en Caliente**:
* Compara el string de la caja contra el patrón `^#[0-9A-Fa-f]{6}$`.
* **Si es correcto**: Pinta el preview del color real y colorea el borde del entry en gris/azul normal (`COLOR_ENTRY_BORDER`).
* **Si es incorrecto**: No actualiza el color y pinta el borde de la caja de texto en rojo de peligro (`COLOR_ERROR`), indicando al usuario que el valor introducido no es válido.

#### `_al_cambiar_fuente(self, valor)`
Callback del selector de letra. Toma la opción (ej: "Grande"), extrae los píxeles base del mapa `TAMANOS_FUENTE` (14px) y reconfigura en caliente el texto de ejemplo (`self.label_preview_fuente.configure(font=...)`), permitiendo al operario verificar si la escala tipográfica se ajusta a su comodidad visual antes de guardar en disco.

#### `_guardar(self)`
Valida de forma atómica todas las variables:
* Si el tema es personalizado, ejecuta `_validar_colores()` cruzando los entries contra la regex Hex. Si alguno es inválido, aborta con un mensaje de alerta en rojo.
* Instancia un objeto `AppConfig` fresco y llama a `guardar_config(nueva)`.
* Detona `self.on_config_changed(nueva)`, aplicando la recarga del tema en caliente en todo el Dashboard.

---

## 2. SelectorColorPopup — Picker Flotante de Colores

### Ubicación del Código
* [selector_color_widget.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/selector_color_widget.py)

### Responsabilidad
Servir como ventana emergente (pop-up) que despliega una paleta estructurada de colores curados para facilitar el diseño del tema personalizado al operario.

### 2.1 Atributos e Interfaz
* `PALETA_COLORES`: Array estático de 48 colores hexadecimales ordenados por tonalidades en 6 filas × 8 columnas (grises, rojos, amarillos, verdes, cyanes, púrpuras y colores base de fondos de SGI Salud).
* `_callback` (`callable`): Función que recibe el color seleccionado.
* `cuadro_preview` (`CTkFrame`): Visualización de gran tamaño del color seleccionado.
* `entrada_hex` (`CTkEntry`): Campo manual de código Hex.

### 2.2 Métodos Críticos
* `__init__()`: Configura la ventana como flotante y sin bordes de sistema operativo (`wm_overrideredirect(True)`), forzando el comportamiento modal.
* `_crear_widgets()`: Dibuja la grilla de 48 botones de CustomTkinter. Cada botón se pinta con su color hexadecimal correspondiente y se asocia a `_seleccionar_de_paleta(hex)`.
* `_posicionar(self, widget_padre)`: **Algoritmo de Posicionamiento Absoluto**: Mide el tamaño requerido del popup y lo posiciona exactamente debajo del entry clicado de la configuración, con validación de desbordamiento de pantalla.
* `_al_perder_foco(self)`: Utiliza `self.focus_get()` para verificar que el ratón no se haya ido a otra ventana externa. Si es así, se auto-destruye preventivamente, logrando un comportamiento de dropdown flotante.

---

## 3. ColoresView — Referencia de Colores del Hospital

### Ubicación del Código
* [colores_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/colores_view.py)

### Responsabilidad
Mostrar una pantalla informativa de solo lectura que detalla la paleta cromática de ordenamiento físico de historias clínicas del hospital.

### 3.1 Atributos y Métodos
* `controller` (instancia de `ColorController`): Enlace para obtener la lista de colores de base de datos.
* `scroll_colores` (`CTkScrollableFrame`): Contenedor con scroll para evitar recortes.
* `_renderizar_colores(self, colores)`: **Algoritmo de Grilla de Dos Columnas**:
  * Utiliza división y módulo matemático sobre el índice del bucle:
    `fila = idx // 2`, `columna = idx % 2`
  * Posiciona las tarjetas con `.grid()` de forma balanceada formando una matriz limpia de 2 columnas × 5 filas.

---

## 4. UsuariosView — Panel Administrativo de Operadores

### Ubicación del Código
* [usuarios_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/usuarios_view.py)

### Responsabilidad
Módulo CRUD completo que permite al administrador registrar, editar, desactivar operarios y reestablecer sus contraseñas mediante validación SHA-256.

### 4.1 Lógica y Comportamientos Clave

#### `_construir_formulario(self, parent)`
Construye las cajas de texto tradicionales (nombre, usuario, clave) y encapsula dentro del frame `self.seccion_cambio_clave` los inputs para reestablecer contraseñas de usuarios existentes.

#### `_seleccionar_usuario(self, usuario)`
**Algoritmo de Carga Dinámica de Edición**:
* Lee el objeto de la fila pulsada e inyecta la información en las cajas del formulario.
* Guarda el ID en `self.id_usuario_seleccionado`.
* **Comportamiento**: Ejecuta `.pack(fill="x")` sobre `self.seccion_cambio_clave`. Esto despliega visualmente la sección de cambio de contraseña en la parte inferior del formulario lateral. Si el formulario se limpia pulsando "Nuevo", el método ejecuta `self.seccion_cambio_clave.pack_forget()`, ocultando la sección para que no estorbe en los nuevos registros.

#### `_cambiar_clave(self)`
Recopila la clave actual, la nueva y su confirmación.
* Llama a `self.controlador.cambiar_clave()`.
* **Seguridad**: El controlador valida que la clave actual sea correcta (hasheando y comparando contra el valor en DB) antes de firmar el hash de la clave nueva.
* Si tiene éxito, limpia las entradas de claves de forma segura y notifica al usuario.
