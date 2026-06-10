"""
Selector visual de color para el tema personalizado.

Popup con paleta de colores predefinidos en cuadrícula, campo hex manual
y preview del color seleccionado. Se abre al hacer clic en un cuadro
de color de la configuración.

Uso::

    def al_seleccionar(hex_color):
        print(hex_color)  # "#FF5500"

    SelectorColorPopup(parent, callback=al_seleccionar, color_inicial="#0F1923")
"""

import customtkinter as ctk


# ══════════════════════════════════════════════════════════════════
#  PALETA DE COLORES CURADOS
# ══════════════════════════════════════════════════════════════════

# 6 filas × 8 columnas = 48 colores, 3 niveles de claridad por tono
PALETA_COLORES = [
    # Fila 1: Grises / Neutros
    "#1A1A2E", "#2D2D44", "#4A4A5A", "#6B6B7B",
    "#8E8E9E", "#B0B0C0", "#D0D0DD", "#F0F0F5",
    # Fila 2: Rojos / Naranjas
    "#4A0E0E", "#8B1A1A", "#DC143C", "#FF4C6A",
    "#7A3300", "#CC5500", "#FF8C00", "#FFB347",
    # Fila 3: Amarillos / Verdes
    "#7A6600", "#B8960F", "#FFD700", "#FFF176",
    "#0D4A0D", "#1B7A1B", "#228B22", "#66BB6A",
    # Fila 4: Cyanes / Azules
    "#004D4D", "#008080", "#40E0D0", "#87CEEB",
    "#0A2647", "#0D47A1", "#1976D2", "#42A5F5",
    # Fila 5: Púrpuras / Rosas
    "#2E0854", "#6A0DAD", "#9C27B0", "#CE93D8",
    "#4A0028", "#880E4F", "#E91E63", "#FF69B4",
    # Fila 6: Tonos especiales (oscuros para fondos)
    "#0F1923", "#141E2B", "#182633", "#1E3044",
    "#00A8E8", "#007BB5", "#00D68F", "#2A4158",
]


class SelectorColorPopup(ctk.CTkToplevel):
    """Popup de selección visual de color.

    Muestra una paleta de 48 colores organizados en una cuadrícula
    clicable, un campo de texto hex para ingreso manual, y un
    preview grande del color actualmente seleccionado.

    Args:
        parent:         Widget padre (se posiciona relativo a él).
        callback:       Función que recibe el hex string al aceptar.
        color_inicial:  Color hex inicial para el preview (default '#0F1923').
        colores_tema:   Dict con claves de color para estilizar el popup.
    """

    def __init__(self, parent, callback, color_inicial="#0F1923", colores_tema=None):
        super().__init__(parent)

        self.wm_overrideredirect(True)
        self.transient(parent)
        self.grab_set()

        self._callback = callback
        self._color_seleccionado = color_inicial

        # Colores del popup
        c = colores_tema or {}
        self._fondo = c.get("panel", "#182633")
        self._entrada_fondo = c.get("entrada_fondo", "#1E3044")
        self._entrada_borde = c.get("entrada_borde", "#2A4158")
        self._texto = c.get("texto", "#E8EDF2")
        self._texto_sec = c.get("texto_secundario", "#8899AA")
        self._acento = c.get("acento", "#00A8E8")
        self._acento_hover = c.get("acento_hover", "#007BB5")
        self._exito = c.get("exito", "#00D68F")
        self._error = c.get("error", "#FF4C6A")

        self.configure(fg_color=self._fondo)
        self._crear_widgets()
        self._posicionar(parent)
        self.bind("<FocusOut>", self._al_perder_foco)

    def _crear_widgets(self):
        """Construye la paleta, preview y botones."""
        # ── Título ──
        ctk.CTkLabel(
            self, text="Seleccionar Color",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self._texto,
        ).pack(padx=12, pady=(10, 6))

        # ── Paleta de colores (8 columnas × 6 filas) ──
        marco_paleta = ctk.CTkFrame(self, fg_color="transparent")
        marco_paleta.pack(padx=10, pady=(0, 8))

        for indice, hex_color in enumerate(PALETA_COLORES):
            fila = indice // 8
            columna = indice % 8
            boton_color = ctk.CTkButton(
                marco_paleta, text="", width=28, height=28,
                corner_radius=4, border_width=1,
                fg_color=hex_color,
                border_color=self._entrada_borde,
                hover_color=hex_color,
                command=lambda h=hex_color: self._seleccionar_de_paleta(h),
            )
            boton_color.grid(row=fila, column=columna, padx=2, pady=2)

        # ── Preview + Campo hex ──
        marco_inferior = ctk.CTkFrame(self, fg_color="transparent")
        marco_inferior.pack(fill="x", padx=10, pady=(0, 6))

        # Preview grande
        self.cuadro_preview = ctk.CTkFrame(
            marco_inferior, fg_color=self._color_seleccionado,
            width=40, height=40, corner_radius=8,
            border_width=1, border_color=self._entrada_borde,
        )
        self.cuadro_preview.pack(side="left", padx=(0, 8))
        self.cuadro_preview.pack_propagate(False)

        # Campo hex manual
        marco_hex = ctk.CTkFrame(marco_inferior, fg_color="transparent")
        marco_hex.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            marco_hex, text="Hex:", anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self._texto_sec,
        ).pack(fill="x")

        self.entrada_hex = ctk.CTkEntry(
            marco_hex, height=28, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self._entrada_fondo,
            border_color=self._entrada_borde,
            text_color=self._texto,
        )
        self.entrada_hex.insert(0, self._color_seleccionado)
        self.entrada_hex.pack(fill="x")
        self.entrada_hex.bind("<KeyRelease>", self._al_escribir_hex)

        # ── Botones Aceptar / Cancelar ──
        marco_botones = ctk.CTkFrame(self, fg_color="transparent")
        marco_botones.pack(fill="x", padx=10, pady=(0, 10))

        estilo_btn = dict(
            height=30, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        )

        ctk.CTkButton(
            marco_botones, text="Aceptar", width=90,
            fg_color=self._exito, hover_color="#00B377",
            text_color="#FFF", command=self._aceptar, **estilo_btn,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            marco_botones, text="Cancelar", width=90,
            fg_color=self._entrada_fondo, hover_color=self._entrada_borde,
            text_color=self._texto_sec, command=self._cancelar, **estilo_btn,
        ).pack(side="left")

    def _seleccionar_de_paleta(self, hex_color):
        """Actualiza la selección al hacer clic en un color de la paleta."""
        self._color_seleccionado = hex_color
        self.cuadro_preview.configure(fg_color=hex_color)
        self.entrada_hex.delete(0, "end")
        self.entrada_hex.insert(0, hex_color)
        self.entrada_hex.configure(border_color=self._entrada_borde)

    def _al_escribir_hex(self, _evento=None):
        """Actualiza el preview al escribir un hex manualmente."""
        import re
        valor = self.entrada_hex.get().strip()
        if re.match(r"^#[0-9A-Fa-f]{6}$", valor):
            self._color_seleccionado = valor
            self.cuadro_preview.configure(fg_color=valor)
            self.entrada_hex.configure(border_color=self._entrada_borde)
        else:
            self.entrada_hex.configure(border_color=self._error)

    def _aceptar(self):
        """Invoca el callback con el color seleccionado y cierra."""
        self._callback(self._color_seleccionado)
        self.grab_release()
        self.destroy()

    def _cancelar(self):
        """Cierra sin invocar el callback."""
        self.grab_release()
        self.destroy()

    def _posicionar(self, widget_padre):
        """Posiciona el popup cerca del widget padre."""
        self.update_idletasks()
        x = widget_padre.winfo_rootx()
        y = widget_padre.winfo_rooty() + widget_padre.winfo_height() + 4
        ancho = self.winfo_reqwidth()
        alto = self.winfo_reqheight()
        if x + ancho > self.winfo_screenwidth():
            x = self.winfo_screenwidth() - ancho - 8
        if y + alto > self.winfo_screenheight():
            y = widget_padre.winfo_rooty() - alto - 4
        self.geometry(f"+{x}+{y}")

    def _al_perder_foco(self, _evento=None):
        """Cierra al perder foco (excepto si fue a un hijo)."""
        try:
            w = self.focus_get()
            if w and str(self) in str(w):
                return
        except KeyError:
            pass
        self.grab_release()
        self.destroy()
