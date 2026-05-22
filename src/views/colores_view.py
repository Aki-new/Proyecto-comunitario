import customtkinter as ctk
from controllers.color_controller import ColorController


class ColoresView(ctk.CTkFrame):
    """Modulo de referencia de colores del hospital.
    Muestra los 10 colores y sus rangos de numero de historia en una
    cuadricula visual de solo lectura.
    """

    # -- Paleta de colores -----------------------------------------------------
    COLOR_BG = "#0F1923"
    COLOR_PANEL = "#182633"
    COLOR_ACCENT = "#00A8E8"
    COLOR_ACCENT_HOVER = "#007BB5"
    COLOR_TEXT = "#E8EDF2"
    COLOR_TEXT_SEC = "#8899AA"
    COLOR_ENTRY_BG = "#1E3044"
    COLOR_ENTRY_BORDER = "#2A4158"
    COLOR_ERROR = "#FF4C6A"
    COLOR_SUCCESS = "#00D68F"
    COLOR_ROW_ALT = "#1A2D3D"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = ColorController()
        self._crear_widgets()
        self._cargar_datos()

    # ==========================================================================
    # Construccion de la interfaz
    # ==========================================================================

    def _crear_widgets(self):
        """Construye la tarjeta de encabezado, la cuadricula de colores
        y la nota informativa.
        """

        # -- Tarjeta de encabezado ---------------------------------------------
        header_card = ctk.CTkFrame(
            self, fg_color=self.COLOR_PANEL,
            corner_radius=12, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )
        header_card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            header_card,
            text="Referencia de Colores",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header_card,
            text=(
                "Cada tarjeta de historia clinica se clasifica por un color "
                "determinado automaticamente segun el ultimo par de digitos del "
                "numero de historia. A continuacion se muestra la tabla completa "
                "de colores y sus rangos correspondientes."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
            wraplength=700,
        ).pack(fill="x", padx=24, pady=(0, 20))

        # -- Mensaje de error (oculto por defecto) -----------------------------
        self.label_mensaje = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_ERROR,
            anchor="w",
        )
        self.label_mensaje.pack(fill="x", padx=4, pady=(0, 4))

        # -- Contenedor de la cuadricula de colores ----------------------------
        self.grid_frame = ctk.CTkFrame(
            self, fg_color="transparent",
        )
        self.grid_frame.pack(fill="both", expand=True, pady=(0, 12))

        # Configurar 2 columnas con peso igual
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

        # -- Nota informativa --------------------------------------------------
        nota_frame = ctk.CTkFrame(
            self, fg_color=self.COLOR_PANEL,
            corner_radius=12, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )
        nota_frame.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            nota_frame,
            text="Nota",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.COLOR_ACCENT,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(14, 2))

        ctk.CTkLabel(
            nota_frame,
            text=(
                "Los colores se asignan automaticamente al registrar una tarjeta. "
                "Se determina por el primer digito (decena) del ultimo par del "
                "numero de historia clinica. Por ejemplo, si el numero es "
                "03-77-34, el ultimo par es 34, la decena es 3, y el color "
                "asignado sera Naranja."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
            wraplength=700,
        ).pack(fill="x", padx=24, pady=(0, 14))

    # ==========================================================================
    # Carga de datos
    # ==========================================================================

    def _cargar_datos(self):
        """Obtiene la referencia de colores del controlador y renderiza las cards."""
        try:
            colores = self.controller.obtener_referencia_colores()
            self._renderizar_colores(colores)
        except Exception as e:
            self.label_mensaje.configure(
                text=f"Error al cargar colores: {e}",
                text_color=self.COLOR_ERROR,
            )

    def _renderizar_colores(self, colores: list[dict]):
        """Crea las tarjetas de color en la cuadricula (2 columnas x 5 filas)."""
        for idx, color_data in enumerate(colores):
            fila = idx // 2
            columna = idx % 2

            card = self._crear_card_color(
                self.grid_frame,
                nombre=color_data["nombre"],
                rango=color_data["rango"],
                hex_color=color_data["hex"],
            )
            card.grid(
                row=fila, column=columna,
                padx=8, pady=8, sticky="nsew",
            )

        # Configurar las filas para que tengan peso
        for fila in range((len(colores) + 1) // 2):
            self.grid_frame.grid_rowconfigure(fila, weight=1)

    def _crear_card_color(
        self, parent, nombre: str, rango: str, hex_color: str
    ) -> ctk.CTkFrame:
        """Crea una tarjeta individual para un color.

        Muestra un cuadro grande coloreado, el nombre del color en negrita
        y el rango de numeros de historia asociado.
        """
        card = ctk.CTkFrame(
            parent, fg_color=self.COLOR_PANEL,
            corner_radius=12, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )

        contenido = ctk.CTkFrame(card, fg_color="transparent")
        contenido.pack(fill="x", padx=20, pady=16)

        # Cuadro de color grande
        cuadro = ctk.CTkFrame(
            contenido, fg_color=hex_color,
            width=60, height=60,
            corner_radius=12,
        )
        cuadro.pack(side="left", padx=(0, 16))
        cuadro.pack_propagate(False)

        # Info del color (nombre + rango)
        info_frame = ctk.CTkFrame(contenido, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info_frame,
            text=nombre,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            info_frame,
            text=f"Rango: {rango}",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        # Hex code (info adicional)
        ctk.CTkLabel(
            info_frame,
            text=hex_color,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        return card
