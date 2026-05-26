"""
Vista de Gestión de Pacientes — SGI Salud.

Módulo unificado que combina búsqueda, listado, registro y edición
de pacientes junto con la creación de su tarjeta índice.

Componentes principales:
    - Barra de búsqueda con criterios múltiples
    - Tabla de resultados con filas clicables
    - Formulario lateral desplegable para CRUD
    - Selector de cédula (V-, E-, S/C)
    - Widget de calendario para fecha de nacimiento
    - Toggle auto/manual para N. de Historia
    - Preview de color en tiempo real

Relación con otros módulos:
    - Usa PacienteController para CRUD de pacientes
    - Usa TarjetaController para CRUD de tarjetas y auto-generación
    - Usa BusquedaController para consultas a la vista SQL
    - Usa CampoFecha (calendario_widget) para selección de fechas
    - Lee AppConfig para el modo de N. Historia (manual/auto)
"""

import customtkinter as ctk
from controllers.paciente_controller import PacienteController
from controllers.tarjeta_controller import TarjetaController
from controllers.busqueda_controller import BusquedaController
from models.config import cargar_config
from models.num_historia_utils import (
    obtener_color_por_num_historia,
    validar_formato_num_historia,
    MAPA_COLORES,
)
from views.calendario_widget import CampoFecha


class PacientesView(ctk.CTkFrame):
    """Módulo unificado de gestión de pacientes.

    Combina búsqueda, listado, registro y edición de pacientes
    con la creación automática de la tarjeta índice.

    Atributos:
        controlador_paciente:       Controlador CRUD de pacientes.
        controlador_tarjeta:        Controlador CRUD de tarjetas.
        controlador_busqueda:       Controlador de búsquedas en vista SQL.
        id_paciente_seleccionado:   ID del paciente cargado en el formulario (None si nuevo).
        id_tarjeta_seleccionada:    ID de la tarjeta del paciente seleccionado (None si no tiene).
        _widgets_filas_tabla:       Lista de frames de filas renderizadas en la tabla.
        _formulario_visible:        Indica si el panel del formulario está desplegado.
        config:                     Configuración de la aplicación (modo historia, etc).
    """

    # ══════════════════════════════════════════════════════════════════
    #  CRITERIOS DE BÚSQUEDA
    # ══════════════════════════════════════════════════════════════════
    CRITERIOS = [
        ("todos",            "Todos"),
        ("cedula",           "Cedula"),
        ("nombre_completo",  "Nombres"),
        ("apellido",         "Apellidos"),
        ("fecha_nacimiento", "Fecha Nacimiento"),
        ("lugar_nacimiento", "Lugar Nacimiento"),
        ("num_historia",     "N. Historia"),
    ]

    # Anchos fijos de columnas en píxeles para alineación
    ANCHOS_COLUMNAS = [90, 180, 85, 110, 80, 100]
    NOMBRES_COLUMNAS = ["Cedula", "Nombre", "F. Nac.", "Lugar Nac.", "N. Historia", "Color"]

    # ══════════════════════════════════════════════════════════════════
    #  CONSTRUCTOR
    # ══════════════════════════════════════════════════════════════════

    def __init__(self, parent, tema=None, fuentes=None, **kwargs):
        """Inicializa la vista de pacientes.

        Args:
            parent:  Widget padre donde se coloca este frame.
            tema:    Dict de colores del tema activo (pasado por dashboard).
            fuentes: Dict de tamaños de fuente activos.
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        # Colores dinámicos desde el tema
        t = tema or {}
        self.COLOR_PANEL = t.get("panel", "#182633")
        self.COLOR_ACCENT = t.get("acento", "#00A8E8")
        self.COLOR_ACCENT_HOVER = t.get("acento_hover", "#007BB5")
        self.COLOR_TEXT = t.get("texto", "#E8EDF2")
        self.COLOR_TEXT_SEC = t.get("texto_secundario", "#8899AA")
        self.COLOR_ENTRY_BG = t.get("entrada_fondo", "#1E3044")
        self.COLOR_ENTRY_BORDER = t.get("entrada_borde", "#2A4158")
        self.COLOR_ERROR = t.get("error", "#FF4C6A")
        self.COLOR_SUCCESS = t.get("exito", "#00D68F")
        self.COLOR_DANGER = t.get("peligro", "#FF4C6A")
        self.COLOR_DANGER_HOVER = t.get("peligro_hover", "#D93A5A")
        self.COLOR_ROW_ALT = t.get("fila_alterna", "#1A2D3D")

        # Tamaños de fuente dinámicos
        f = fuentes or {}
        self.F_BASE = f.get("base", 12)
        self.F_TITULO = f.get("titulo", 16)
        self.F_SUBTITULO = f.get("subtitulo", 14)
        self.F_ETIQUETA = f.get("etiqueta", 11)
        # Derivados para tabla (1 nivel menor que base para caber más datos)
        self.F_TABLA = max(self.F_BASE - 2, 9)
        self.F_TABLA_HEADER = max(self.F_BASE - 1, 10)

        self.controlador_paciente = PacienteController()
        self.controlador_tarjeta = TarjetaController()
        self.controlador_busqueda = BusquedaController()
        self.id_paciente_seleccionado: int | None = None
        self.id_tarjeta_seleccionada: int | None = None
        self._widgets_filas_tabla: list[ctk.CTkFrame] = []
        self._formulario_visible = False
        self.config = cargar_config()
        self._construir_interfaz()
        self._buscar_todos()

    # ══════════════════════════════════════════════════════════════════
    #  CONSTRUCCIÓN DE LA INTERFAZ
    # ══════════════════════════════════════════════════════════════════

    def _construir_interfaz(self):
        """Construye todos los elementos de la interfaz:
        barra de búsqueda, info, cuerpo (tabla + formulario).
        """
        # ── Barra de búsqueda (compacta, altura fija 42px) ──
        barra_busqueda = ctk.CTkFrame(
            self, fg_color=self.COLOR_PANEL, corner_radius=8, height=42
        )
        barra_busqueda.pack(fill="x", pady=(0, 3))
        barra_busqueda.pack_propagate(False)

        ctk.CTkLabel(
            barra_busqueda, text="Buscar:",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
            text_color=self.COLOR_TEXT_SEC,
        ).pack(side="left", padx=(10, 4))

        # Dropdown de criterio de búsqueda
        self.variable_criterio_busqueda = ctk.StringVar(value="Todos")
        ctk.CTkOptionMenu(
            barra_busqueda, variable=self.variable_criterio_busqueda,
            values=[criterio[1] for criterio in self.CRITERIOS],
            width=145, height=26, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.COLOR_ENTRY_BG, button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            dropdown_fg_color=self.COLOR_PANEL,
            dropdown_hover_color=self.COLOR_ENTRY_BG,
            text_color=self.COLOR_TEXT,
            command=self._al_cambiar_criterio,
        ).pack(side="left", padx=(0, 4))

        # Campo de texto de búsqueda
        self.entrada_busqueda = ctk.CTkEntry(
            barra_busqueda, placeholder_text="Ingrese valor de busqueda...",
            height=26, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.COLOR_ENTRY_BG, border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT,
            placeholder_text_color=self.COLOR_TEXT_SEC,
        )
        self.entrada_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.entrada_busqueda.bind("<Return>", lambda _: self._ejecutar_busqueda())
        self.entrada_busqueda.bind("<KeyRelease>", self._busqueda_en_vivo)
        self._id_debounce_busqueda = None

        # Botones de la barra
        estilo_boton_barra = dict(
            height=26, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
        )

        ctk.CTkButton(
            barra_busqueda, text="Buscar", width=65,
            fg_color=self.COLOR_ACCENT, hover_color=self.COLOR_ACCENT_HOVER,
            text_color="#FFF", command=self._ejecutar_busqueda,
            **estilo_boton_barra,
        ).pack(side="left", padx=(0, 8))

        # Separador vertical
        ctk.CTkFrame(
            barra_busqueda, fg_color=self.COLOR_ENTRY_BORDER, width=1
        ).pack(side="left", fill="y", pady=8, padx=(0, 8))

        ctk.CTkButton(
            barra_busqueda, text="+ Nuevo Ingreso", width=120,
            fg_color=self.COLOR_SUCCESS, hover_color="#00B377",
            text_color="#FFF", command=self._nuevo_ingreso,
            **estilo_boton_barra,
        ).pack(side="left", padx=(0, 10))

        # ── Línea de información (mensaje + conteo) ──
        marco_info = ctk.CTkFrame(self, fg_color="transparent", height=18)
        marco_info.pack(fill="x", pady=(0, 2))
        marco_info.pack_propagate(False)

        self.etiqueta_mensaje = ctk.CTkLabel(
            marco_info, text="", anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_TEXT_SEC,
        )
        self.etiqueta_mensaje.pack(side="left", padx=4)

        self.etiqueta_conteo = ctk.CTkLabel(
            marco_info, text="", anchor="e",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_TEXT_SEC,
        )
        self.etiqueta_conteo.pack(side="right", padx=4)

        # ── Cuerpo principal (tabla + formulario) ──
        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.pack(fill="both", expand=True)
        self.cuerpo.grid_columnconfigure(0, weight=1)
        self.cuerpo.grid_rowconfigure(0, weight=1)

        self._construir_tabla(self.cuerpo)
        self._construir_formulario(self.cuerpo)

    # ── TABLA ─────────────────────────────────────────────────────────

    def _construir_tabla(self, parent):
        """Construye el panel de la tabla con header y área scrollable.

        El header está DENTRO del scroll para garantizar alineación
        perfecta con las filas de datos.

        Args:
            parent: Widget padre (self.cuerpo).
        """
        self.panel_tabla = ctk.CTkFrame(
            parent, fg_color=self.COLOR_PANEL,
            corner_radius=8, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )
        self.panel_tabla.grid(row=0, column=0, sticky="nsew")
        self.panel_tabla.grid_rowconfigure(0, weight=1)
        self.panel_tabla.grid_columnconfigure(0, weight=1)

        self.tabla_scroll = ctk.CTkScrollableFrame(
            self.panel_tabla, fg_color="transparent",
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ACCENT,
        )
        self.tabla_scroll.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        # Configurar columnas con anchos fijos
        for indice, ancho in enumerate(self.ANCHOS_COLUMNAS):
            self.tabla_scroll.grid_columnconfigure(indice, weight=1, minsize=ancho)

        # Header embebido en el scroll
        fila_cabecera = ctk.CTkFrame(
            self.tabla_scroll, fg_color=self.COLOR_ENTRY_BG,
            corner_radius=4, height=28,
        )
        fila_cabecera.grid(
            row=0, column=0,
            columnspan=len(self.NOMBRES_COLUMNAS),
            sticky="ew", pady=(0, 3),
        )
        fila_cabecera.grid_propagate(False)

        for indice, (nombre, ancho) in enumerate(
            zip(self.NOMBRES_COLUMNAS, self.ANCHOS_COLUMNAS)
        ):
            fila_cabecera.grid_columnconfigure(indice, weight=1, minsize=ancho)
            ctk.CTkLabel(
                fila_cabecera, text=nombre,
                font=ctk.CTkFont(family="Segoe UI", size=self.F_TABLA_HEADER, weight="bold"),
                text_color=self.COLOR_TEXT_SEC, anchor="w",
            ).grid(row=0, column=indice, sticky="ew", padx=6, pady=5)

    # ── FORMULARIO ────────────────────────────────────────────────────

    def _construir_formulario(self, parent):
        """Construye el panel del formulario lateral (oculto por defecto).

        Incluye: título, botones de acción, campos del paciente,
        selector de cédula, campo de fecha con calendario, sección
        de tarjeta con toggle auto/manual, y preview de color.

        Args:
            parent: Widget padre (self.cuerpo).
        """
        self.panel_formulario = ctk.CTkFrame(
            parent, fg_color=self.COLOR_PANEL,
            corner_radius=8, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )

        # ── Título del formulario + botón cerrar ──
        marco_titulo_formulario = ctk.CTkFrame(
            self.panel_formulario, fg_color="transparent"
        )
        marco_titulo_formulario.pack(fill="x", padx=10, pady=(8, 0))

        self.etiqueta_titulo_formulario = ctk.CTkLabel(
            marco_titulo_formulario, text="Nuevo Ingreso",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.COLOR_TEXT, anchor="w",
        )
        self.etiqueta_titulo_formulario.pack(side="left")

        ctk.CTkButton(
            marco_titulo_formulario, text="X", width=26, height=22,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=self.COLOR_ENTRY_BG,
            hover_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_SEC,
            command=self._cerrar_formulario,
        ).pack(side="right")

        # ── Botones de acción del formulario ──
        barra_botones_formulario = ctk.CTkFrame(
            self.panel_formulario, fg_color="transparent"
        )
        barra_botones_formulario.pack(fill="x", padx=10, pady=(6, 2))

        estilo_boton_form = dict(
            height=26, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
        )

        ctk.CTkButton(
            barra_botones_formulario, text="Guardar", width=70,
            fg_color=self.COLOR_SUCCESS, hover_color="#00B377",
            text_color="#FFF", command=self._guardar_paciente,
            **estilo_boton_form,
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            barra_botones_formulario, text="Eliminar", width=70,
            fg_color=self.COLOR_DANGER, hover_color=self.COLOR_DANGER_HOVER,
            text_color="#FFF", command=self._eliminar_paciente,
            **estilo_boton_form,
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            barra_botones_formulario, text="Limpiar", width=60,
            fg_color=self.COLOR_ENTRY_BG,
            hover_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_SEC,
            command=self._limpiar_formulario,
            **estilo_boton_form,
        ).pack(side="left")

        # ── Separador ──
        ctk.CTkFrame(
            self.panel_formulario, fg_color=self.COLOR_ENTRY_BORDER, height=1
        ).pack(fill="x", padx=10, pady=(4, 2))

        # ── Área scrollable del formulario ──
        scroll_formulario = ctk.CTkScrollableFrame(
            self.panel_formulario, fg_color="transparent",
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ENTRY_BORDER,
        )
        scroll_formulario.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # Estilos reutilizables para entries y labels del formulario
        estilo_entrada = dict(
            height=30, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            fg_color=self.COLOR_ENTRY_BG,
            border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT,
            placeholder_text_color=self.COLOR_TEXT_SEC,
        )
        estilo_etiqueta = dict(
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
            text_color=self.COLOR_TEXT_SEC, anchor="w",
        )

        # Diccionario para almacenar los entries del formulario
        self.entradas_formulario: dict[str, ctk.CTkEntry] = {}

        # ── Sección: Datos del Paciente ──
        ctk.CTkLabel(
            scroll_formulario, text="DATOS DEL PACIENTE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=self.COLOR_ACCENT, anchor="w",
        ).pack(fill="x", padx=4, pady=(2, 4))

        # Cédula con selector de tipo (V-, E-, S/C)
        ctk.CTkLabel(
            scroll_formulario, text="Cedula", **estilo_etiqueta
        ).pack(fill="x", padx=4, pady=(2, 1))

        marco_cedula = ctk.CTkFrame(scroll_formulario, fg_color="transparent")
        marco_cedula.pack(fill="x", padx=4, pady=(0, 2))

        self.selector_tipo_cedula = ctk.CTkOptionMenu(
            marco_cedula, values=["V-", "E-", "S/C"], width=60, height=30,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.COLOR_ENTRY_BG, button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            dropdown_fg_color=self.COLOR_PANEL,
            dropdown_hover_color=self.COLOR_ENTRY_BG,
            text_color=self.COLOR_TEXT,
            command=self._al_cambiar_tipo_cedula,
        )
        self.selector_tipo_cedula.set("V-")
        self.selector_tipo_cedula.pack(side="left", padx=(0, 4))

        self.entrada_numero_cedula = ctk.CTkEntry(
            marco_cedula, placeholder_text="12345678", **estilo_entrada
        )
        self.entrada_numero_cedula.pack(side="left", fill="x", expand=True)

        # Campos de texto del paciente
        campos_paciente = [
            ("Primer Nombre *", "nombre1", ""),
            ("Segundo Nombre", "nombre2", "(Opcional)"),
            ("Primer Apellido *", "apellido1", ""),
            ("Segundo Apellido", "apellido2", "(Opcional)"),
            ("Lugar de Nacimiento *", "lugar_nacimiento", ""),
        ]
        for texto_label, clave, placeholder in campos_paciente:
            ctk.CTkLabel(
                scroll_formulario, text=texto_label, **estilo_etiqueta
            ).pack(fill="x", padx=4, pady=(3, 1))
            entrada = ctk.CTkEntry(
                scroll_formulario, placeholder_text=placeholder, **estilo_entrada
            )
            entrada.pack(fill="x", padx=4, pady=(0, 1))
            self.entradas_formulario[clave] = entrada

        # Fecha de nacimiento con widget de calendario
        ctk.CTkLabel(
            scroll_formulario, text="Fecha de Nacimiento *", **estilo_etiqueta
        ).pack(fill="x", padx=4, pady=(3, 1))
        self.campo_fecha_nacimiento = CampoFecha(scroll_formulario)
        self.campo_fecha_nacimiento.pack(fill="x", padx=4, pady=(0, 1))

        # Estado vital (dropdown)
        ctk.CTkLabel(
            scroll_formulario, text="Estado Vital", **estilo_etiqueta
        ).pack(fill="x", padx=4, pady=(3, 1))
        self.selector_estado_vital = ctk.CTkOptionMenu(
            scroll_formulario, values=["Vivo", "Fallecido"], height=30,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.COLOR_ENTRY_BG, button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_TEXT,
            dropdown_fg_color=self.COLOR_PANEL,
            dropdown_hover_color=self.COLOR_ENTRY_BG,
        )
        self.selector_estado_vital.set("Vivo")
        self.selector_estado_vital.pack(fill="x", padx=4, pady=(0, 1))

        # ── Separador entre paciente y tarjeta ──
        ctk.CTkFrame(
            scroll_formulario, fg_color=self.COLOR_ENTRY_BORDER, height=1
        ).pack(fill="x", padx=4, pady=6)

        # ── Sección: Tarjeta Índice ──
        ctk.CTkLabel(
            scroll_formulario, text="TARJETA INDICE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=self.COLOR_ACCENT, anchor="w",
        ).pack(fill="x", padx=4, pady=(0, 4))

        # Toggle Manual / Auto para N. Historia
        ctk.CTkLabel(
            scroll_formulario, text="Modo de ingreso", **estilo_etiqueta
        ).pack(fill="x", padx=4, pady=(0, 1))

        self.modo_historia = ctk.CTkSegmentedButton(
            scroll_formulario, values=["Manual", "Auto"],
            font=ctk.CTkFont(family="Segoe UI", size=10),
            fg_color=self.COLOR_ENTRY_BG,
            selected_color=self.COLOR_ACCENT,
            selected_hover_color=self.COLOR_ACCENT_HOVER,
            unselected_color=self.COLOR_ENTRY_BG,
            unselected_hover_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT,
            command=self._al_cambiar_modo_historia,
        )
        modo_inicial = "Auto" if self.config.modo_num_historia == "auto" else "Manual"
        self.modo_historia.set(modo_inicial)
        self.modo_historia.pack(fill="x", padx=4, pady=(0, 3))

        # Campo de N. Historia
        ctk.CTkLabel(
            scroll_formulario, text="N. Historia * (XX-XX-XX)", **estilo_etiqueta
        ).pack(fill="x", padx=4, pady=(0, 1))
        self.entrada_num_historia = ctk.CTkEntry(
            scroll_formulario, placeholder_text="Ej: 03-77-34", **estilo_entrada
        )
        self.entrada_num_historia.pack(fill="x", padx=4, pady=(0, 3))
        self.entrada_num_historia.bind(
            "<KeyRelease>", lambda _: self._actualizar_preview_color()
        )

        # Preview de color (cuadrado + nombre)
        self.marco_preview_color = ctk.CTkFrame(
            scroll_formulario, fg_color=self.COLOR_ENTRY_BG,
            corner_radius=6, height=32,
        )
        self.marco_preview_color.pack(fill="x", padx=4, pady=(0, 3))
        self.marco_preview_color.pack_propagate(False)

        marco_interior_preview = ctk.CTkFrame(
            self.marco_preview_color, fg_color="transparent"
        )
        marco_interior_preview.pack(fill="x", padx=8, pady=4)

        self.cuadro_color_preview = ctk.CTkFrame(
            marco_interior_preview, fg_color="#444",
            width=18, height=18, corner_radius=4,
        )
        self.cuadro_color_preview.pack(side="left", padx=(0, 6))
        self.cuadro_color_preview.pack_propagate(False)

        self.etiqueta_nombre_color = ctk.CTkLabel(
            marco_interior_preview, text="Ingrese N. Historia",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_TEXT_SEC,
        )
        self.etiqueta_nombre_color.pack(side="left")

        # Etiqueta de errores de validación
        self.etiqueta_errores = ctk.CTkLabel(
            scroll_formulario, text="", wraplength=260, anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_ERROR,
        )
        self.etiqueta_errores.pack(fill="x", padx=4, pady=(2, 2))

    # ══════════════════════════════════════════════════════════════════
    #  MOSTRAR / OCULTAR FORMULARIO
    # ══════════════════════════════════════════════════════════════════

    def _mostrar_formulario(self, titulo="Nuevo Ingreso"):
        """Despliega el panel del formulario lateral.

        Reduce la tabla al 55% del ancho y muestra el formulario al 45%.

        Args:
            titulo: Texto a mostrar en el encabezado del formulario.
        """
        if self._formulario_visible:
            self.etiqueta_titulo_formulario.configure(text=titulo)
            return
        self._formulario_visible = True
        self.etiqueta_titulo_formulario.configure(text=titulo)
        self.cuerpo.grid_columnconfigure(0, weight=55)
        self.cuerpo.grid_columnconfigure(1, weight=45)
        self.panel_formulario.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def _cerrar_formulario(self):
        """Oculta el formulario y devuelve la tabla al 100% del ancho.

        Limpia el formulario y resetea la selección.
        """
        if not self._formulario_visible:
            return
        self._formulario_visible = False
        self.id_paciente_seleccionado = None
        self.id_tarjeta_seleccionada = None
        self._limpiar_formulario()
        self.panel_formulario.grid_forget()
        self.cuerpo.grid_columnconfigure(0, weight=1)
        self.cuerpo.grid_columnconfigure(1, weight=0)

    # ══════════════════════════════════════════════════════════════════
    #  MANEJO DE CÉDULA
    # ══════════════════════════════════════════════════════════════════

    def _al_cambiar_tipo_cedula(self, valor):
        """Callback cuando el usuario cambia el tipo de cédula (V-, E-, S/C).

        Si selecciona S/C, desactiva el campo numérico.

        Args:
            valor: Opción seleccionada ("V-", "E-", "S/C").
        """
        if valor == "S/C":
            self.entrada_numero_cedula.delete(0, "end")
            self.entrada_numero_cedula.configure(
                state="disabled", placeholder_text="Sin cedula"
            )
        else:
            self.entrada_numero_cedula.configure(
                state="normal", placeholder_text="12345678"
            )

    def _obtener_cedula_completa(self) -> str:
        """Construye la cédula completa a partir del selector + campo numérico.

        Returns:
            String con la cédula (ej: 'V-12345678', 'S/C', o '' si vacía).
        """
        tipo = self.selector_tipo_cedula.get()
        if tipo == "S/C":
            return "S/C"
        numero = self.entrada_numero_cedula.get().strip()
        return f"{tipo}{numero}" if numero else ""

    def _establecer_cedula(self, cedula: str):
        """Carga una cédula en el selector + campo numérico.

        Determina el tipo (V-, E-, S/C) y separa la parte numérica.

        Args:
            cedula: Cédula completa (ej: 'V-12345678', 'E-98765432', 'S/C').
        """
        if not cedula or cedula == "S/C":
            self.selector_tipo_cedula.set("S/C")
            self.entrada_numero_cedula.configure(
                state="disabled", placeholder_text="Sin cedula"
            )
            self.entrada_numero_cedula.delete(0, "end")
        elif cedula.upper().startswith("E-"):
            self.selector_tipo_cedula.set("E-")
            self.entrada_numero_cedula.configure(
                state="normal", placeholder_text="12345678"
            )
            self._establecer_texto_entrada(self.entrada_numero_cedula, cedula[2:])
        else:
            self.selector_tipo_cedula.set("V-")
            self.entrada_numero_cedula.configure(
                state="normal", placeholder_text="12345678"
            )
            inicio = 2 if cedula.upper().startswith("V-") else 0
            self._establecer_texto_entrada(
                self.entrada_numero_cedula, cedula[inicio:]
            )

    # ══════════════════════════════════════════════════════════════════
    #  MODO N. HISTORIA (AUTO / MANUAL)
    # ══════════════════════════════════════════════════════════════════

    def _al_cambiar_modo_historia(self, valor):
        """Callback al cambiar entre modo Manual y Auto para N. de Historia.

        En modo Auto, pre-llena el campo con el siguiente número secuencial.
        En modo Manual, limpia el campo para ingreso libre.

        Args:
            valor: "Manual" o "Auto".
        """
        if valor == "Auto":
            siguiente = self.controlador_tarjeta.generar_siguiente_num_historia()
            self._establecer_texto_entrada(self.entrada_num_historia, siguiente)
            self._actualizar_preview_color()
        else:
            self.entrada_num_historia.delete(0, "end")
            self._actualizar_preview_color()

    # ══════════════════════════════════════════════════════════════════
    #  BÚSQUEDA
    # ══════════════════════════════════════════════════════════════════

    def _al_cambiar_criterio(self, valor):
        """Callback al cambiar el criterio de búsqueda.

        Si se selecciona 'Todos', ejecuta la búsqueda automáticamente.

        Args:
            valor: Texto del criterio seleccionado.
        """
        if valor == "Todos":
            self.entrada_busqueda.delete(0, "end")
            self._buscar_todos()

    def _buscar_todos(self):
        """Ejecuta una búsqueda sin filtros (muestra todos los pacientes)."""
        try:
            self._renderizar_resultados(self.controlador_busqueda.obtener_todos())
        except Exception as error:
            self._mostrar_mensaje(f"Error: {error}", True)

    def _ejecutar_busqueda(self):
        """Ejecuta la búsqueda según el criterio y valor ingresados.

        Lee el criterio del dropdown y el texto del campo de búsqueda,
        luego llama al controlador correspondiente.
        Si el campo está vacío, muestra todos los resultados.
        """
        criterio_texto = self.variable_criterio_busqueda.get()
        clave_criterio = next(
            (clave for clave, label in self.CRITERIOS if label == criterio_texto),
            "todos",
        )
        valor = self.entrada_busqueda.get().strip()

        # Si no hay texto, mostrar todos
        if not valor:
            self._buscar_todos()
            return

        exito, resultado = self.controlador_busqueda.buscar(clave_criterio, valor)
        if exito:
            self._renderizar_resultados(resultado)
            self.etiqueta_mensaje.configure(text="")
        else:
            self._mostrar_mensaje(str(resultado), True)

    def _busqueda_en_vivo(self, _evento=None):
        """Búsqueda en tiempo real con debounce de 300ms.

        Cancela el timer anterior y programa uno nuevo. Esto evita
        hacer consultas a la BD en cada tecla presionada.
        """
        if self._id_debounce_busqueda:
            self.after_cancel(self._id_debounce_busqueda)
        self._id_debounce_busqueda = self.after(300, self._ejecutar_busqueda)

    def _renderizar_resultados(self, registros):
        """Renderiza los resultados de búsqueda como filas en la tabla.

        Destruye las filas anteriores y crea nuevas con los datos recibidos.
        Si no hay resultados, muestra un mensaje con opción de registrar.

        Args:
            registros: Lista de TarjetaSalida con los datos a mostrar.
        """
        # Limpiar filas anteriores
        for widget_fila in self._widgets_filas_tabla:
            widget_fila.destroy()
        self._widgets_filas_tabla.clear()

        cantidad = len(registros)
        self.etiqueta_conteo.configure(
            text=f"{cantidad} resultado{'s' if cantidad != 1 else ''}"
        )

        if not registros:
            self._renderizar_sin_resultados()
            return

        for indice, registro in enumerate(registros):
            color_fila = self.COLOR_ROW_ALT if indice % 2 == 0 else "transparent"
            marco_fila = ctk.CTkFrame(
                self.tabla_scroll, fg_color=color_fila,
                corner_radius=3, height=28,
            )
            marco_fila.grid(
                row=indice + 1, column=0,
                columnspan=len(self.NOMBRES_COLUMNAS),
                sticky="ew", pady=1,
            )
            marco_fila.grid_propagate(False)

            for indice_col, ancho in enumerate(self.ANCHOS_COLUMNAS):
                marco_fila.grid_columnconfigure(
                    indice_col, weight=1, minsize=ancho
                )

            # Construir nombre completo
            nombre_completo = registro.nombre1
            if registro.nombre2:
                nombre_completo += f" {registro.nombre2}"
            nombre_completo += f" {registro.apellido1}"
            if registro.apellido2:
                nombre_completo += f" {registro.apellido2}"

            hex_color = self._obtener_hex_color(registro.num_historia)
            valores_columna = [
                registro.cedula, nombre_completo,
                registro.fecha_nacimiento, registro.lugar_nacimiento,
                registro.num_historia, None,
            ]

            for indice_col, valor_celda in enumerate(valores_columna):
                if indice_col == 5:  # Columna Color (indicador visual)
                    marco_color = ctk.CTkFrame(
                        marco_fila, fg_color="transparent"
                    )
                    marco_color.grid(
                        row=0, column=indice_col, sticky="ew", padx=4, pady=2
                    )
                    indicador_color = ctk.CTkFrame(
                        marco_color, fg_color=hex_color,
                        width=12, height=12, corner_radius=3,
                    )
                    indicador_color.pack(side="left", padx=(0, 3))
                    indicador_color.pack_propagate(False)
                    etiqueta_color = ctk.CTkLabel(
                        marco_color, text=registro.color or "",
                        font=ctk.CTkFont(family="Segoe UI", size=self.F_TABLA),
                        text_color=self.COLOR_TEXT, anchor="w",
                    )
                    etiqueta_color.pack(side="left")
                    marco_color.bind(
                        "<Button-1>",
                        lambda _, r=registro: self._seleccionar_paciente(r),
                    )
                    etiqueta_color.bind(
                        "<Button-1>",
                        lambda _, r=registro: self._seleccionar_paciente(r),
                    )
                else:
                    etiqueta_celda = ctk.CTkLabel(
                        marco_fila, text=str(valor_celda or ""),
                        font=ctk.CTkFont(family="Segoe UI", size=self.F_TABLA),
                        text_color=self.COLOR_TEXT, anchor="w",
                    )
                    etiqueta_celda.grid(
                        row=0, column=indice_col,
                        sticky="ew", padx=6, pady=3,
                    )
                    etiqueta_celda.bind(
                        "<Button-1>",
                        lambda _, r=registro: self._seleccionar_paciente(r),
                    )

            marco_fila.bind(
                "<Button-1>",
                lambda _, r=registro: self._seleccionar_paciente(r),
            )
            self._widgets_filas_tabla.append(marco_fila)

    def _renderizar_sin_resultados(self):
        """Muestra un mensaje cuando no hay resultados, con botón para registrar."""
        marco_vacio = ctk.CTkFrame(self.tabla_scroll, fg_color="transparent")
        marco_vacio.grid(
            row=1, column=0,
            columnspan=len(self.NOMBRES_COLUMNAS),
            pady=30, sticky="ew",
        )
        ctk.CTkLabel(
            marco_vacio, text="No se encontraron pacientes",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.COLOR_TEXT_SEC,
        ).pack(pady=(0, 8))

        ctk.CTkButton(
            marco_vacio, text="Registrar Nuevo Paciente",
            width=180, height=30, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=self.COLOR_SUCCESS, hover_color="#00B377",
            text_color="#FFF", command=self._nuevo_ingreso,
        ).pack()

        self._widgets_filas_tabla.append(marco_vacio)

    # ══════════════════════════════════════════════════════════════════
    #  ACCIONES (CRUD)
    # ══════════════════════════════════════════════════════════════════

    def _nuevo_ingreso(self):
        """Prepara el formulario para registrar un nuevo paciente.

        Limpia todos los campos, resetea la selección y despliega el formulario.
        Si el modo de N. Historia es 'Auto', pre-llena el campo.
        """
        self.id_paciente_seleccionado = None
        self.id_tarjeta_seleccionada = None
        self._limpiar_formulario()
        self._mostrar_formulario("Nuevo Ingreso")
        self.entradas_formulario["nombre1"].focus_set()

        # Pre-llenar N. Historia si el modo es Auto
        if self.modo_historia.get() == "Auto":
            siguiente = self.controlador_tarjeta.generar_siguiente_num_historia()
            self._establecer_texto_entrada(self.entrada_num_historia, siguiente)
            self._actualizar_preview_color()

    def _seleccionar_paciente(self, registro):
        """Carga los datos de un paciente de la tabla en el formulario.

        Busca el paciente por id_paciente (funciona con múltiples S/C),
        carga su tarjeta si existe, y abre el formulario en modo edición.

        Args:
            registro: Objeto TarjetaSalida con los datos del paciente.
        """
        paciente = self.controlador_paciente.obtener_paciente_por_id(
            registro.id_paciente
        )
        if not paciente:
            self._mostrar_mensaje("No se pudo cargar el paciente.", True)
            return

        self.id_paciente_seleccionado = paciente.id
        tarjeta = self.controlador_tarjeta.obtener_tarjeta_paciente(paciente.id)
        self.id_tarjeta_seleccionada = tarjeta.id if tarjeta else None

        # Llenar campos del formulario
        self._establecer_cedula(paciente.cedula)
        self._establecer_texto_entrada(
            self.entradas_formulario["nombre1"], paciente.nombre1
        )
        self._establecer_texto_entrada(
            self.entradas_formulario["nombre2"], paciente.nombre2 or ""
        )
        self._establecer_texto_entrada(
            self.entradas_formulario["apellido1"], paciente.apellido1
        )
        self._establecer_texto_entrada(
            self.entradas_formulario["apellido2"], paciente.apellido2 or ""
        )
        self.campo_fecha_nacimiento.establecer_fecha(paciente.fecha_nacimiento)
        self._establecer_texto_entrada(
            self.entradas_formulario["lugar_nacimiento"], paciente.lugar_nacimiento
        )
        self.selector_estado_vital.set(
            "Vivo" if paciente.estado_vital == 1 else "Fallecido"
        )

        if tarjeta:
            self._establecer_texto_entrada(
                self.entrada_num_historia, tarjeta.num_historia
            )
        else:
            self.entrada_num_historia.delete(0, "end")

        self._actualizar_preview_color()
        self._mostrar_formulario("Editar Paciente")

    def _guardar_paciente(self):
        """Guarda o actualiza un paciente según el estado del formulario.

        Si id_paciente_seleccionado es None, registra un nuevo paciente
        con tarjeta. Si tiene valor, actualiza el paciente y su tarjeta.
        """
        datos = self._recoger_datos_formulario()
        if datos is None:
            return

        datos_paciente, num_historia = datos
        try:
            if self.id_paciente_seleccionado is not None:
                # Modo edición: actualizar paciente + tarjeta
                exito, mensaje = self.controlador_paciente.actualizar_paciente(
                    self.id_paciente_seleccionado, datos_paciente
                )
                if not exito:
                    self._mostrar_mensaje(mensaje, True)
                    return

                if self.id_tarjeta_seleccionada is not None:
                    exito_tarjeta, mensaje_tarjeta = (
                        self.controlador_tarjeta.actualizar_tarjeta(
                            self.id_tarjeta_seleccionada, num_historia
                        )
                    )
                else:
                    exito_tarjeta, mensaje_tarjeta = (
                        self.controlador_tarjeta.crear_tarjeta(
                            self.id_paciente_seleccionado, num_historia
                        )
                    )

                if not exito_tarjeta:
                    self._mostrar_mensaje(
                        f"Paciente OK. Tarjeta: {mensaje_tarjeta}", True
                    )
                else:
                    self._mostrar_mensaje(
                        "Paciente y tarjeta actualizados.", False
                    )
            else:
                # Modo nuevo: registrar paciente + tarjeta
                exito, mensaje = (
                    self.controlador_paciente.registrar_paciente_con_tarjeta(
                        datos_paciente, num_historia
                    )
                )
                self._mostrar_mensaje(mensaje, not exito)

            if exito:
                self._limpiar_formulario()
                self.id_paciente_seleccionado = None
                self.id_tarjeta_seleccionada = None
                self._buscar_todos()
        except Exception as error:
            self._mostrar_mensaje(f"Error: {error}", True)

    def _eliminar_paciente(self):
        """Desactiva (borrado lógico) el paciente seleccionado y su tarjeta."""
        if self.id_paciente_seleccionado is None:
            self._mostrar_mensaje(
                "Seleccione un paciente de la lista primero.", True
            )
            return
        try:
            if self.id_tarjeta_seleccionada:
                self.controlador_tarjeta.eliminar_tarjeta(
                    self.id_tarjeta_seleccionada
                )
            exito, mensaje = self.controlador_paciente.eliminar_paciente(
                self.id_paciente_seleccionado
            )
            self._mostrar_mensaje(mensaje, not exito)
            if exito:
                self._cerrar_formulario()
                self._buscar_todos()
        except Exception as error:
            self._mostrar_mensaje(f"Error: {error}", True)

    # ══════════════════════════════════════════════════════════════════
    #  PREVIEW DE COLOR EN TIEMPO REAL
    # ══════════════════════════════════════════════════════════════════

    def _actualizar_preview_color(self):
        """Actualiza el cuadrado de color y el nombre según el N. Historia.

        Lee el valor actual del campo de N. Historia, valida el formato,
        y muestra el color correspondiente o un mensaje de error.
        """
        num_historia = self.entrada_num_historia.get().strip()
        if not num_historia or not validar_formato_num_historia(num_historia):
            self.cuadro_color_preview.configure(fg_color="#444")
            texto = (
                "Formato requerido: XX-XX-XX" if num_historia
                else "Ingrese N. Historia"
            )
            self.etiqueta_nombre_color.configure(
                text=texto, text_color=self.COLOR_TEXT_SEC
            )
            return
        try:
            info_color = obtener_color_por_num_historia(num_historia)
            self.cuadro_color_preview.configure(fg_color=info_color["hex"])
            self.etiqueta_nombre_color.configure(
                text=info_color["nombre"], text_color=self.COLOR_TEXT
            )
        except ValueError:
            self.cuadro_color_preview.configure(fg_color="#444")
            self.etiqueta_nombre_color.configure(
                text="Formato invalido", text_color=self.COLOR_ERROR
            )

    # ══════════════════════════════════════════════════════════════════
    #  VALIDACIÓN Y RECOLECCIÓN DE DATOS
    # ══════════════════════════════════════════════════════════════════

    def _recoger_datos_formulario(self):
        """Valida y recolecta todos los datos del formulario.

        Verifica cada campo obligatorio y muestra errores específicos
        si alguno no cumple los requisitos.

        Returns:
            Tupla (dict_datos_paciente, num_historia) si todo es válido,
            o None si hay errores de validación.
        """
        errores = []

        cedula = self._obtener_cedula_completa()
        if not cedula:
            errores.append("• Cedula: ingrese el numero o seleccione S/C.")

        nombre1 = self.entradas_formulario["nombre1"].get().strip()
        if not nombre1:
            errores.append("• Primer Nombre: campo obligatorio.")

        apellido1 = self.entradas_formulario["apellido1"].get().strip()
        if not apellido1:
            errores.append("• Primer Apellido: campo obligatorio.")

        fecha = self.campo_fecha_nacimiento.obtener_fecha().strip()
        if not fecha:
            errores.append("• Fecha Nac.: campo obligatorio (DD/MM/AAAA).")
        elif not self._validar_formato_fecha(fecha):
            errores.append("• Fecha Nac.: formato invalido. Ejemplo: 21/02/2000.")

        lugar = self.entradas_formulario["lugar_nacimiento"].get().strip()
        if not lugar:
            errores.append("• Lugar Nac.: campo obligatorio.")

        num_historia = self.entrada_num_historia.get().strip()
        if not num_historia:
            errores.append("• N. Historia: campo obligatorio (XX-XX-XX).")
        elif not validar_formato_num_historia(num_historia):
            errores.append(
                "• N. Historia: use 3 pares de digitos (ej: 03-77-34)."
            )

        if errores:
            self.etiqueta_errores.configure(text="\n".join(errores))
            return None

        self.etiqueta_errores.configure(text="")

        return {
            "cedula": cedula,
            "nombre1": nombre1,
            "nombre2": (
                self.entradas_formulario["nombre2"].get().strip() or None
            ),
            "apellido1": apellido1,
            "apellido2": (
                self.entradas_formulario["apellido2"].get().strip() or None
            ),
            "fecha_nacimiento": fecha.replace("-", "/"),
            "lugar_nacimiento": lugar,
            "estado_vital": (
                1 if self.selector_estado_vital.get() == "Vivo" else 0
            ),
        }, num_historia

    @staticmethod
    def _validar_formato_fecha(valor: str) -> bool:
        """Valida que una fecha tenga formato DD/MM/AAAA o DD-MM-AAAA.

        Verifica que día, mes y año sean valores lógicos.

        Args:
            valor: String con la fecha a validar.

        Returns:
            True si el formato y valores son válidos.
        """
        import re
        if not re.match(r"^\d{2}[/\-]\d{2}[/\-]\d{4}$", valor):
            return False
        valor = valor.replace("-", "/")
        partes = valor.split("/")
        dia, mes, anio = int(partes[0]), int(partes[1]), int(partes[2])
        return 1 <= dia <= 31 and 1 <= mes <= 12 and 1900 <= anio <= 2100

    # ══════════════════════════════════════════════════════════════════
    #  UTILIDADES
    # ══════════════════════════════════════════════════════════════════

    @staticmethod
    def _establecer_texto_entrada(entrada, valor):
        """Limpia un CTkEntry y establece un nuevo valor.

        Args:
            entrada: Widget CTkEntry a modificar.
            valor: Texto a colocar en el entry.
        """
        entrada.delete(0, "end")
        entrada.insert(0, str(valor))

    def _limpiar_formulario(self):
        """Resetea todos los campos del formulario a su estado inicial.

        Limpia entries, selectores, campo de fecha, preview de color
        y mensajes de error.
        """
        for entrada in self.entradas_formulario.values():
            entrada.configure(state="normal")
            entrada.delete(0, "end")
        self.entrada_numero_cedula.configure(state="normal")
        self.entrada_numero_cedula.delete(0, "end")
        self.entrada_num_historia.delete(0, "end")
        self.campo_fecha_nacimiento.limpiar()
        self.selector_estado_vital.set("Vivo")
        self.selector_tipo_cedula.set("V-")
        self.entrada_numero_cedula.configure(placeholder_text="12345678")
        self.cuadro_color_preview.configure(fg_color="#444")
        self.etiqueta_nombre_color.configure(
            text="Ingrese N. Historia", text_color=self.COLOR_TEXT_SEC
        )
        self.etiqueta_errores.configure(text="")

    def _mostrar_mensaje(self, texto: str, es_error: bool = False):
        """Muestra un mensaje en la barra de información.

        Args:
            texto: Mensaje a mostrar.
            es_error: True para color rojo, False para color verde.
        """
        color = self.COLOR_ERROR if es_error else self.COLOR_SUCCESS
        if not texto:
            color = self.COLOR_TEXT_SEC
        self.etiqueta_mensaje.configure(text=texto, text_color=color)

    @staticmethod
    def _obtener_hex_color(num_historia: str) -> str:
        """Obtiene el código hexadecimal del color según el N. de Historia.

        Args:
            num_historia: Número de historia en formato XX-XX-XX.

        Returns:
            Código hex del color (ej: '#FF8C00'), o '#666' si es inválido.
        """
        try:
            decena = int(num_historia.split("-")[2][0])
            _, hex_color = MAPA_COLORES[decena]
            return hex_color
        except (IndexError, ValueError, KeyError):
            return "#666"
