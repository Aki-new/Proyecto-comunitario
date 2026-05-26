"""
Vista de Referencia de Colores — SGI Salud.

Muestra los 10 colores del sistema y sus rangos de número de historia
en una cuadrícula visual de solo lectura con scroll para responsive.

Acepta tema y fuentes dinámicos pasados desde el dashboard.
"""

import customtkinter as ctk
from controllers.color_controller import ColorController


class ColoresView(ctk.CTkFrame):
    """Módulo de referencia de colores del hospital.

    Muestra los 10 colores y sus rangos de número de historia en una
    cuadrícula visual de 2 columnas × 5 filas.

    Args:
        parent:  Widget padre.
        tema:    Dict de colores del tema activo.
        fuentes: Dict de tamaños de fuente activos.
    """

    def __init__(self, parent, tema=None, fuentes=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        # Colores dinámicos
        t = tema or {}
        self.COLOR_BG = t.get("fondo", "#0F1923")
        self.COLOR_PANEL = t.get("panel", "#182633")
        self.COLOR_ACCENT = t.get("acento", "#00A8E8")
        self.COLOR_TEXT = t.get("texto", "#E8EDF2")
        self.COLOR_TEXT_SEC = t.get("texto_secundario", "#8899AA")
        self.COLOR_ENTRY_BG = t.get("entrada_fondo", "#1E3044")
        self.COLOR_ENTRY_BORDER = t.get("entrada_borde", "#2A4158")
        self.COLOR_ERROR = t.get("error", "#FF4C6A")

        self.controller = ColorController()
        self._crear_widgets()
        self._cargar_datos()

    # ══════════════════════════════════════════════════════════════════
    #  INTERFAZ
    # ══════════════════════════════════════════════════════════════════

    def _crear_widgets(self):
        """Encabezado, cuadrícula scrollable y nota informativa."""

        # ── Encabezado ──
        header = ctk.CTkFrame(
            self, fg_color=self.COLOR_PANEL, corner_radius=12,
            border_width=1, border_color=self.COLOR_ENTRY_BORDER,
        )
        header.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            header, text="Referencia de Colores",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.COLOR_TEXT, anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 2))

        ctk.CTkLabel(
            header,
            text=(
                "Cada tarjeta de historia clínica se clasifica por un color "
                "determinado automáticamente según el último par de dígitos "
                "del número de historia."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_TEXT_SEC, anchor="w", wraplength=600,
        ).pack(fill="x", padx=20, pady=(0, 16))

        # ── Mensaje de error ──
        self.label_mensaje = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_ERROR, anchor="w",
        )
        self.label_mensaje.pack(fill="x", padx=4, pady=(0, 4))

        # ── Contenedor scrollable para las tarjetas de colores ──
        self.scroll_colores = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ACCENT,
        )
        self.scroll_colores.pack(fill="both", expand=True, pady=(0, 8))
        self.scroll_colores.grid_columnconfigure(0, weight=1)
        self.scroll_colores.grid_columnconfigure(1, weight=1)

        # ── Nota informativa ──
        nota = ctk.CTkFrame(
            self, fg_color=self.COLOR_PANEL, corner_radius=10,
            border_width=1, border_color=self.COLOR_ENTRY_BORDER,
        )
        nota.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            nota, text="Nota",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.COLOR_ACCENT, anchor="w",
        ).pack(fill="x", padx=20, pady=(10, 2))

        ctk.CTkLabel(
            nota,
            text=(
                "Los colores se asignan automáticamente al registrar una tarjeta. "
                "Se determina por la decena del último par del número de historia. "
                "Ejemplo: 03-77-34 → último par 34 → decena 3 → Naranja."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_TEXT_SEC, anchor="w", wraplength=550,
        ).pack(fill="x", padx=20, pady=(0, 10))

    # ══════════════════════════════════════════════════════════════════
    #  CARGA DE DATOS
    # ══════════════════════════════════════════════════════════════════

    def _cargar_datos(self):
        """Obtiene la referencia de colores y renderiza las cards."""
        try:
            colores = self.controller.obtener_referencia_colores()
            self._renderizar_colores(colores)
        except Exception as e:
            self.label_mensaje.configure(
                text=f"Error al cargar colores: {e}",
                text_color=self.COLOR_ERROR,
            )

    def _renderizar_colores(self, colores: list[dict]):
        """Crea las tarjetas en la cuadrícula scrollable (2 col × 5 filas)."""
        for idx, color_data in enumerate(colores):
            fila = idx // 2
            columna = idx % 2
            card = self._crear_card_color(
                self.scroll_colores,
                nombre=color_data["nombre"],
                rango=color_data["rango"],
                hex_color=color_data["hex"],
            )
            card.grid(row=fila, column=columna, padx=6, pady=6, sticky="nsew")

        for fila in range((len(colores) + 1) // 2):
            self.scroll_colores.grid_rowconfigure(fila, weight=1)

    def _crear_card_color(self, parent, nombre, rango, hex_color):
        """Crea una tarjeta individual para un color."""
        card = ctk.CTkFrame(
            parent, fg_color=self.COLOR_PANEL, corner_radius=10,
            border_width=1, border_color=self.COLOR_ENTRY_BORDER,
        )

        contenido = ctk.CTkFrame(card, fg_color="transparent")
        contenido.pack(fill="x", padx=16, pady=12)

        # Cuadro de color
        cuadro = ctk.CTkFrame(
            contenido, fg_color=hex_color,
            width=50, height=50, corner_radius=10,
        )
        cuadro.pack(side="left", padx=(0, 12))
        cuadro.pack_propagate(False)

        # Info
        info = ctk.CTkFrame(contenido, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info, text=nombre,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            info, text=f"Rango: {rango}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_TEXT_SEC, anchor="w",
        ).pack(fill="x", pady=(1, 0))

        ctk.CTkLabel(
            info, text=hex_color,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_TEXT_SEC, anchor="w",
        ).pack(fill="x", pady=(1, 0))

        return card
