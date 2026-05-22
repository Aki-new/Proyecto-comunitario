import customtkinter as ctk
from models.usuario import Usuario


class DashboardView(ctk.CTkToplevel):
    """Panel principal del sistema (Dashboard).
    Contiene un menú lateral con navegación y un área de contenido
    principal donde se cargarán los distintos módulos.
    """

    # ── Paleta de colores ──────────────────────────────────────────
    COLOR_BG = "#0F1923"
    COLOR_SIDEBAR = "#141E2B"
    COLOR_SIDEBAR_BORDER = "#1E3044"
    COLOR_CONTENT = "#182633"
    COLOR_ACCENT = "#00A8E8"
    COLOR_ACCENT_HOVER = "#007BB5"
    COLOR_TEXT = "#E8EDF2"
    COLOR_TEXT_SEC = "#8899AA"
    COLOR_TEXT_DIM = "#4A6275"
    COLOR_BTN_HOVER = "#1E3044"
    COLOR_HEADER = "#141E2B"
    COLOR_SEPARATOR = "#1E3044"
    COLOR_DANGER = "#FF4C6A"
    COLOR_DANGER_HOVER = "#D93A5A"

    # ── Opciones del menú lateral ─────────────────────────────────
    MENU_ITEMS = [
        {"texto": "📊  Inicio",          "clave": "inicio"},
        {"texto": "👤  Pacientes",        "clave": "pacientes"},
        {"texto": "🗂️  Tarjetas",         "clave": "tarjetas"},
        {"texto": "🔍  Búsqueda",         "clave": "busqueda"},
        {"texto": "🎨  Colores",          "clave": "colores"},
        {"texto": "👥  Usuarios",         "clave": "usuarios"},
    ]

    def __init__(self, master, usuario: Usuario, on_logout: callable):
        """
        Args:
            master: Ventana raíz (CTk).
            usuario: Objeto Usuario con los datos del usuario autenticado.
            on_logout: Callback que se ejecuta al cerrar sesión.
        """
        super().__init__(master)
        self.usuario = usuario
        self.on_logout = on_logout
        self.menu_seleccionado = "inicio"
        self.botones_menu: dict[str, ctk.CTkButton] = {}

        self._configurar_ventana()
        self._crear_layout()
        self._mostrar_pagina_inicio()

        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)

    # ── Configuración de ventana ──────────────────────────────────
    def _configurar_ventana(self):
        self.title(
            "Sistema de Gestión — Hospital Dr. Armando Delgado Montero"
        )
        self.configure(fg_color=self.COLOR_BG)

        # Tamaño y centrado
        ancho, alto = 1100, 680
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.minsize(900, 550)

    # ── Layout principal ──────────────────────────────────────────
    def _crear_layout(self):
        # Contenedor principal con grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar fija
        self.grid_columnconfigure(1, weight=1)  # Contenido expande
        self.grid_rowconfigure(0, weight=1)

        self._crear_sidebar()
        self._crear_area_contenido()

    # ── Sidebar ───────────────────────────────────────────────────
    def _crear_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_SIDEBAR,
            corner_radius=0,
            width=240,
            border_width=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # ── Header del sidebar (info del hospital) ──
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(20, 8))

        icono = ctk.CTkFrame(
            header, fg_color=self.COLOR_ACCENT,
            corner_radius=12, width=42, height=42,
        )
        icono.pack(side="left", padx=(0, 12))
        icono.pack_propagate(False)

        ctk.CTkLabel(
            icono, text="🏥", font=ctk.CTkFont(size=20),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info_frame,
            text="SGI Salud",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            info_frame,
            text="Hospital DADM",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x")

        # ── Separador ──
        ctk.CTkFrame(
            self.sidebar, fg_color=self.COLOR_SEPARATOR, height=1,
        ).pack(fill="x", padx=16, pady=(16, 12))

        # ── Label de sección ──
        ctk.CTkLabel(
            self.sidebar,
            text="MENÚ PRINCIPAL",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=self.COLOR_TEXT_DIM,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(4, 8))

        # ── Botones del menú ──
        for item in self.MENU_ITEMS:
            btn = ctk.CTkButton(
                self.sidebar,
                text=item["texto"],
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                fg_color="transparent",
                hover_color=self.COLOR_BTN_HOVER,
                text_color=self.COLOR_TEXT_SEC,
                anchor="w",
                command=lambda c=item["clave"]: self._seleccionar_menu(c),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.botones_menu[item["clave"]] = btn

        # Marcar "Inicio" como activo
        self._actualizar_estilo_menu("inicio")

        # ── Spacer para empujar perfil y logout al fondo ──
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # ── Separador inferior ──
        ctk.CTkFrame(
            self.sidebar, fg_color=self.COLOR_SEPARATOR, height=1,
        ).pack(fill="x", padx=16, pady=(0, 12))

        # ── Perfil del usuario ──
        perfil_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        perfil_frame.pack(fill="x", padx=16, pady=(0, 8))

        avatar = ctk.CTkFrame(
            perfil_frame, fg_color=self.COLOR_ACCENT,
            corner_radius=20, width=36, height=36,
        )
        avatar.pack(side="left", padx=(0, 10))
        avatar.pack_propagate(False)

        iniciales = (
            self.usuario.nombre[0].upper() + self.usuario.apellido[0].upper()
        )
        ctk.CTkLabel(
            avatar, text=iniciales,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.5, anchor="center")

        user_info = ctk.CTkFrame(perfil_frame, fg_color="transparent")
        user_info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            user_info,
            text=f"{self.usuario.nombre} {self.usuario.apellido}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            user_info,
            text=f"@{self.usuario.usuario}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x")

        # ── Botón cerrar sesión ──
        self.btn_logout = ctk.CTkButton(
            self.sidebar,
            text="🚪  Cerrar Sesión",
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=self.COLOR_DANGER,
            hover_color=self.COLOR_DANGER_HOVER,
            text_color="#FFFFFF",
            command=self._cerrar_sesion,
        )
        self.btn_logout.pack(fill="x", padx=12, pady=(4, 16))

    # ── Área de contenido ─────────────────────────────────────────
    def _crear_area_contenido(self):
        self.area_contenido = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_BG,
            corner_radius=0,
        )
        self.area_contenido.grid(row=0, column=1, sticky="nsew", padx=(0, 0))

        # ── Header del contenido ──
        self.header_contenido = ctk.CTkFrame(
            self.area_contenido,
            fg_color=self.COLOR_HEADER,
            corner_radius=0,
            height=56,
        )
        self.header_contenido.pack(fill="x")
        self.header_contenido.pack_propagate(False)

        self.label_titulo_pagina = ctk.CTkLabel(
            self.header_contenido,
            text="Inicio",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        )
        self.label_titulo_pagina.pack(side="left", padx=24, pady=12)

        # ── Contenedor donde se cargarán los módulos ──
        self.contenedor_pagina = ctk.CTkFrame(
            self.area_contenido,
            fg_color="transparent",
        )
        self.contenedor_pagina.pack(fill="both", expand=True, padx=20, pady=20)

    # ── Navegación del menú ───────────────────────────────────────
    def _seleccionar_menu(self, clave: str):
        """Cambia la sección activa del dashboard."""
        if clave == self.menu_seleccionado:
            return

        self.menu_seleccionado = clave
        self._actualizar_estilo_menu(clave)
        self._limpiar_contenido()

        # Títulos legibles para el header
        titulos = {
            "inicio": "Inicio",
            "pacientes": "Gestión de Pacientes",
            "tarjetas": "Tarjetas de Salud",
            "busqueda": "Búsqueda de Registros",
            "colores": "Gestión de Colores",
            "usuarios": "Gestión de Usuarios",
        }
        self.label_titulo_pagina.configure(text=titulos.get(clave, clave))

        # Cargar la página correspondiente
        paginas = {
            "inicio": self._mostrar_pagina_inicio,
        }
        pagina_fn = paginas.get(clave, self._mostrar_pagina_placeholder)
        pagina_fn()

    def _actualizar_estilo_menu(self, clave_activa: str):
        """Resalta el botón del menú activo y resetea los demás."""
        for clave, btn in self.botones_menu.items():
            if clave == clave_activa:
                btn.configure(
                    fg_color=self.COLOR_ACCENT,
                    text_color="#FFFFFF",
                    hover_color=self.COLOR_ACCENT_HOVER,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.COLOR_TEXT_SEC,
                    hover_color=self.COLOR_BTN_HOVER,
                )

    def _limpiar_contenido(self):
        """Destruye todos los widgets dentro del contenedor de página."""
        for widget in self.contenedor_pagina.winfo_children():
            widget.destroy()

    # ── Páginas de contenido ──────────────────────────────────────
    def _mostrar_pagina_inicio(self):
        """Página de bienvenida con tarjetas de resumen."""
        # ── Mensaje de bienvenida ──
        bienvenida_frame = ctk.CTkFrame(
            self.contenedor_pagina, fg_color=self.COLOR_CONTENT,
            corner_radius=14, border_width=1,
            border_color=self.COLOR_SIDEBAR_BORDER,
        )
        bienvenida_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            bienvenida_frame,
            text=f"Bienvenido/a, {self.usuario.nombre} {self.usuario.apellido}",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            bienvenida_frame,
            text="Sistema de Gestión de Información Estadística y Registros de Salud",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 20))

        # ── Tarjetas de resumen (cards) ──
        cards_frame = ctk.CTkFrame(
            self.contenedor_pagina, fg_color="transparent",
        )
        cards_frame.pack(fill="x", pady=(0, 20))

        cards_data = [
            {"titulo": "Pacientes",  "icono": "👤", "desc": "Registro y gestión"},
            {"titulo": "Tarjetas",   "icono": "🗂️", "desc": "Historias clínicas"},
            {"titulo": "Búsqueda",   "icono": "🔍", "desc": "Consultar registros"},
            {"titulo": "Colores",    "icono": "🎨", "desc": "Clasificación"},
        ]

        for i, card_data in enumerate(cards_data):
            cards_frame.grid_columnconfigure(i, weight=1)
            card = self._crear_card_resumen(
                cards_frame,
                card_data["titulo"],
                card_data["icono"],
                card_data["desc"],
            )
            card.grid(row=0, column=i, padx=6, pady=0, sticky="nsew")

        # ── Información del sistema ──
        info_frame = ctk.CTkFrame(
            self.contenedor_pagina, fg_color=self.COLOR_CONTENT,
            corner_radius=14, border_width=1,
            border_color=self.COLOR_SIDEBAR_BORDER,
        )
        info_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            info_frame,
            text="ℹ️  Acerca del sistema",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(16, 4))

        ctk.CTkLabel(
            info_frame,
            text=(
                "Utilice el menú lateral para navegar entre los distintos "
                "módulos del sistema. Cada sección le permitirá gestionar "
                "los registros correspondientes."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
            wraplength=600,
        ).pack(fill="x", padx=24, pady=(0, 16))

    def _crear_card_resumen(
        self, parent, titulo: str, icono: str, descripcion: str
    ) -> ctk.CTkFrame:
        """Crea una tarjeta de resumen visual para la página de inicio."""
        card = ctk.CTkFrame(
            parent, fg_color=self.COLOR_CONTENT,
            corner_radius=12, border_width=1,
            border_color=self.COLOR_SIDEBAR_BORDER,
            height=120,
        )
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text=icono,
            font=ctk.CTkFont(size=28),
        ).pack(padx=16, pady=(16, 4), anchor="w")

        ctk.CTkLabel(
            card, text=titulo,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 2))

        ctk.CTkLabel(
            card, text=descripcion,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_TEXT_SEC, anchor="w",
        ).pack(fill="x", padx=16)

        return card

    def _mostrar_pagina_placeholder(self):
        """Página temporal para módulos que aún no están implementados."""
        placeholder = ctk.CTkFrame(
            self.contenedor_pagina, fg_color=self.COLOR_CONTENT,
            corner_radius=14, border_width=1,
            border_color=self.COLOR_SIDEBAR_BORDER,
        )
        placeholder.pack(fill="both", expand=True)

        ctk.CTkLabel(
            placeholder, text="🚧",
            font=ctk.CTkFont(size=48),
        ).pack(pady=(60, 10))

        ctk.CTkLabel(
            placeholder,
            text="Módulo en Construcción",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.COLOR_TEXT,
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            placeholder,
            text="Esta sección estará disponible próximamente.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.COLOR_TEXT_SEC,
        ).pack()

    # ── Acciones ──────────────────────────────────────────────────
    def _cerrar_sesion(self):
        """Cierra sesión y ejecuta el callback de logout."""
        self.destroy()
        self.on_logout()

    def _on_cerrar(self):
        """Al cerrar la ventana principal, se cierra toda la aplicación."""
        self.master.destroy()

    # ── Método público para cargar contenido externo ──────────────
    def cargar_modulo(self, clave: str, widget_class, **kwargs):
        """Permite registrar e instanciar módulos externos en el área de contenido.

        Args:
            clave: Clave del menú asociada.
            widget_class: Clase del widget/frame a instanciar.
            **kwargs: Argumentos adicionales para el constructor del widget.
        """
        self._limpiar_contenido()
        modulo = widget_class(self.contenedor_pagina, **kwargs)
        modulo.pack(fill="both", expand=True)
