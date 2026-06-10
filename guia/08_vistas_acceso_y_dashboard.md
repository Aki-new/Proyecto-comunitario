# 🖥️ Guía 8: Detalle de Vistas de Acceso y Dashboard — SGI Salud

Esta guía detalla el funcionamiento interno, variables, métodos y comportamientos de las dos ventanas principales que articulan el ciclo de vida de la interfaz de usuario en SGI Salud: **LoginView** (acceso modal) y **DashboardView** (contenedor principal y orquestador de temas).

---

## 1. LoginView — Ventana de Acceso Modal

### Ubicación del Código
* [login_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/login_view.py)

### Responsabilidad
Autenticar al operador mediante credenciales cifradas (SHA-256) antes de permitir el acceso al sistema. Se ejecuta de forma estrictamente modal sobre una ventana raíz invisible, capturando el foco de la pantalla.

### 1.1 Atributos y Variables de Clase
* **Paleta de Colores de Estilo Local**:
  * `COLOR_BG_DARK` (`"#0F1923"`): Color del lienzo base de la ventana.
  * `COLOR_PANEL` (`"#182633"`): Fondo del recuadro central (card).
  * `COLOR_ACCENT` (`"#00A8E8"`): Color cian para el botón de acción principal e ícono del hospital.
  * `COLOR_ACCENT_HOVER` (`"#007BB5"`): Color al pasar el cursor sobre el botón.
  * `COLOR_ENTRY_BG` (`"#1E3044"`): Fondo oscuro de los campos de entrada de datos.
  * `COLOR_ENTRY_BORDER` (`"#2A4158"`): Bordes de delimitación de los entries y el card.
  * `COLOR_ERROR` (`"#FF4C6A"`): Rojo brillante para notificaciones de credenciales incorrectas.
  * `COLOR_SUCCESS` (`"#00D68F"`): Verde brillante para mensajes de bienvenida exitosa.
* **Variables de Control de Flujo**:
  * `auth_controller` (instancia de `AuthController`): Enlace con la capa de negocio de inicio de sesión.
  * `on_login_success` (`callable`): Callback inyectado por `main.py` para abrir el Dashboard.
  * `panel` (`CTkFrame`): Contenedor visual del formulario.
  * `entry_usuario` (`CTkEntry`): Input de texto plano para el nombre de usuario.
  * `entry_clave` (`CTkEntry`): Input protegido con caracteres de máscara (`●`) para la contraseña.
  * `label_mensaje` (`CTkLabel`): Zona interactiva de texto para alertar errores o éxitos.
  * `btn_login` (`CTkButton`): Botón para enviar las credenciales.

### 1.2 Métodos del Módulo

#### `__init__(self, master, on_login_success: callable)`
Constructor que hereda de `ctk.CTkToplevel` (ventana secundaria de Tkinter). 
* Registra el callback de redirección en `self.on_login_success`.
* Invoca la construcción visual de widgets.
* Intercepta el cierre forzado de la ventana del sistema operativo vinculándolo a `_on_cerrar`.
* Programa una tarea diferida (`self.after(100, ...)`) para darle foco automático con `.focus_set()` al campo `entry_usuario` al renderizar la ventana.

#### `_configurar_ventana(self)`
Define propiedades del sistema operativo:
* Asigna el título y color de fondo.
* Desactiva el redimensionamiento con `self.resizable(False, False)`.
* Calcula el centro absoluto de la pantalla física dividiendo a la mitad las dimensiones del monitor (`self.winfo_screenwidth()`) y posiciona allí la geometría `480x580` de la ventana.
* Bloquea la interacción del sistema operativo con cualquier otra ventana ejecutando `self.grab_set()` (hace la ventana estrictamente modal).

#### `_crear_widgets(self)`
Construye la jerarquía visual de CustomTkinter:
* Instancia el card central (`self.panel`) usando coordenadas relativas `.place(relx=0.5, rely=0.5, anchor="center")`.
* Agrega etiquetas, un ícono emoji en un marco redondeado, y los dos entries.
* Vincula el evento de teclado `<Return>` (Enter): si el foco está en el usuario, salta a la contraseña; si está en la contraseña, ejecuta directamente el intento de login.

#### `_intentar_login(self)`
Captura los strings crudos de los entries y bloquea el botón principal pintando `"Verificando..."` para evitar clics repetidos.
* Llama a `self.auth_controller.login(usuario, clave)`.
* **Si el login es exitoso**: Muestra el mensaje en verde (`COLOR_SUCCESS`) y espera 800ms antes de llamar a `_login_exitoso()` para que el operario perciba la confirmación visual.
* **Si el login falla**: Muestra el error en rojo (`COLOR_ERROR`), rehabilita el botón a su estado normal y detona la micro-animación `_efecto_shake()` sobre el entry de contraseña.

#### `_login_exitoso(self)`
Obtiene el objeto de operario autenticado desde el controlador, libera el bloqueo de pantalla del sistema operativo (`self.grab_release()`), destruye la ventana de Login (`self.destroy()`) y detona el callback `on_login_success` pasándole el usuario.

#### `_efecto_shake(self, widget, veces=4, distancia=8, velocidad=40)`
**Algoritmo de micro-animación premium**:
* Dado que los layouts con `.pack` no permiten variar coordenadas `X` directas, el método implementa una función interna recursiva `paso(i)` que utiliza `self.after` para variar el padding izquierdo y derecho de manera alternada (`padx=(36 + offset, 36 - offset)`).
* Produce un efecto físico de sacudida visual que denota error de forma moderna. Al terminar las iteraciones, restaura el padding original.

#### `_on_cerrar(self)`
Garantiza que si el usuario cierra el login pulsando la "X" de la ventana, la aplicación completa se detenga destruyendo la raíz oculta (`self.master.destroy()`).

---

## 2. DashboardView — Contenedor Principal y Hot-Reloading de Temas

### Ubicación del Código
* [dashboard_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/dashboard_view.py)

### Responsabilidad
Servir como espacio de trabajo unificado tras el inicio de sesión. Administra un menú lateral responsivo de navegación, un header dinámico de sección, y un contenedor de módulos que implementa la inyección de dependencias de temas y su actualización en caliente (hot-reloads).

### 2.1 Atributos y Variables de Clase
* `MENU_ITEMS`: Array estático de diccionarios que define la etiqueta del botón y su identificador lógico de navegación (`inicio`, `pacientes`, `colores`, `usuarios`, `configuracion`).
* `usuario` (`Usuario`): Datos del operador activo en sesión.
* `on_logout` (`callable`): Callback para destruir el dashboard y regresar al Login.
* `menu_seleccionado` (`str`): Identificador del frame activo actual (por defecto `"inicio"`).
* `botones_menu` (`dict[str, CTkButton]`): Mapa indexador de los botones del menú lateral.
* `config` (`AppConfig`): Configuración activa cargada del JSON.
* `colores` (`dict`): Variables activas del tema de colores resuelto.
* `fuentes` (`dict`): Escalas tipográficas en píxeles activas.

### 2.2 Métodos del Módulo

#### `__init__(self, master, usuario: Usuario, on_logout: callable)`
Constructor principal.
* Inicializa la ventana secundaria master.
* Carga la configuración del JSON en disco e invoca `_cargar_colores_desde_config()`.
* Ejecuta la división grid del layout principal y renderiza la pantalla de bienvenida de inicio.

#### `_cargar_colores_desde_config(self)`
Llama a las funciones puras de los modelos para actualizar los diccionarios de variables de diseño:
* `self.colores = obtener_tema(self.config)`
* `self.fuentes = obtener_tamano_fuente(self.config)`

#### `aplicar_tema(self, nueva_config: AppConfig)`
**Algoritmo Clave de Hot-Reloading (Recarga en Caliente)**:
Cuando el usuario modifica el tema visual (ej: cambia de Oscuro a Claro) en el panel de configuración y guarda, este método reconfigura de forma reactiva toda la aplicación en caliente sin necesidad de reiniciarla:
1. Re-lee la configuración y computa la nueva paleta visual.
2. Actualiza el color de fondo de la ventana raíz.
3. Destruye físicamente el widget sidebar anterior (`self.sidebar.destroy()`).
4. Re-ejecuta `_crear_sidebar()`, que instancia el sidebar de CustomTkinter con las nuevas variables del tema (fondos, botones, separadores y avatares se dibujan en frío con el nuevo color).
5. Actualiza la cabecera y el área de contenido (`self.area_contenido.configure(...)`).
6. Limpia la pantalla central activa (`self._limpiar_contenido()`) y re-instancia el módulo activo pasándole los nuevos diccionarios de colores y tipografías. El operario ve un rediseño de interfaz en milisegundos.

#### `_configurar_ventana(self)`
Establece las dimensiones base del Dashboard (`1100x700`), calcula su centrado e impone dimensiones mínimas de resiliencia (`850x520`) para prevenir que se rompa el layout responsivo si el usuario achica demasiado la ventana.

#### `_crear_layout(self)`
Divide la ventana principal en una cuadrícula de 1 fila × 2 columnas:
* **Columna 0**: Ancho adaptable fijo (peso 0) dedicado al menú lateral (`self.sidebar`).
* **Columna 1**: Ancho expandible al máximo disponible (peso 1) para el contenido de los módulos (`self.area_contenido`).

#### `_crear_sidebar(self)`
Construye la barra de herramientas lateral.
* Crea el frame contenedor y su header de hospital.
* Agrega un `CTkScrollableFrame` intermedio. Esto garantiza que si la aplicación se ejecuta en pantallas de baja resolución (netbooks), el menú lateral pueda scrollear internamente sin recortar la cabecera del usuario ni el botón de logout.
* Genera los botones del menú basándose en la constante `MENU_ITEMS`.
* Dibuja un widget de avatar compuesto: toma las primeras letras del Nombre y Apellido del operario, las convierte a mayúsculas y las pinta de blanco sobre un fondo cian (ej: `"Juan Pérez"` -> avatar `"JP"`), personalizando la interfaz de forma dinámica.

#### `_crear_area_contenido(self)`
Dibuja el lienzo del costado derecho.
* Crea una franja superior (Header) que informa al operario el nombre del módulo actual.
* Crea el frame contenedor `self.contenedor_pagina`, que servirá de lienzo dinámico para empacar las pantallas de los módulos.

#### `_seleccionar_menu(self, clave: str)`
Disparador de la barra de navegación:
* Si la pestaña ya está activa, aborta.
* Limpia los widgets del frame de contenido actual (`self._limpiar_contenido()`).
* Actualiza los botones resaltando con color cian el nuevo botón activo y devolviendo a transparentes los inactivos con `_actualizar_estilo_menu()`.
* Instancia el Frame correspondiente inyectándolo en el lienzo central.

#### `_cargar_modulo_vista(self, vista_class)`
Implementa **Inyección de Dependencias**: instancia la clase del módulo visual (ej: `PacientesView`, `ColoresView`) inyectándole de forma obligatoria los mapas dinámicos de colores y fuentes activos del Dashboard:
`vista_class(self.contenedor_pagina, tema=self.colores, fuentes=self.fuentes)`

#### `_mostrar_configuracion(self)`
Carga en el lienzo el frame de configuración, inyectando adicionalmente el callback `self._on_config_changed` para escuchar los cambios en el tema.

#### `_mostrar_pagina_inicio(self)`
Renderiza la pantalla home (Dashboard estadístico). Crea tres cards informativos y responsivos usando Grid Layout que presentan los tres ejes principales de SGI Salud (Pacientes, Colores y Usuarios).
