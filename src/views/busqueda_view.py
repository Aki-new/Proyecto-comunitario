import customtkinter as ctk
from controllers.busqueda_controller import BusquedaController
from models.num_historia_utils import MAPA_COLORES


class BusquedaView(ctk.CTkFrame):
    """Modulo de busqueda de registros (pacientes + tarjetas + colores).
    Permite filtrar por cedula, nombre completo, apellido, fecha y lugar
    de nacimiento. El N. de historia es un resultado, no un filtro.
    """

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

    CRITERIOS = [
        ("todos",            "Todos"),
        ("cedula",           "Cedula"),
        ("nombre_completo",  "Nombre Completo"),
        ("apellido",         "Apellido"),
        ("fecha_nacimiento", "Fecha de Nacimiento"),
        ("lugar_nacimiento", "Lugar de Nacimiento"),
    ]

    COLUMNAS = [
        {"texto": "Cedula",       "peso": 2, "min": 90},
        {"texto": "Nombre",       "peso": 3, "min": 130},
        {"texto": "F. Nac.",      "peso": 1, "min": 85},
        {"texto": "Lugar Nac.",   "peso": 2, "min": 100},
        {"texto": "Estado",       "peso": 1, "min": 60},
        {"texto": "N. Historia",  "peso": 1, "min": 85},
        {"texto": "Color",        "peso": 2, "min": 90},
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = BusquedaController()
        self._filas: list[ctk.CTkFrame] = []
        self._crear_widgets()
        self._cargar_datos()

    # ==========================================================================
    #  UI
    # ==========================================================================

    def _crear_widgets(self):
        # -- Barra de busqueda --
        barra = ctk.CTkFrame(self, fg_color=self.COLOR_PANEL, corner_radius=12,
                             border_width=1, border_color=self.COLOR_ENTRY_BORDER)
        barra.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(barra, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(inner, text="Buscar por:",
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=self.COLOR_TEXT_SEC,
                     ).pack(side="left", padx=(0, 6))

        self._criterio_var = ctk.StringVar(value="Todos")
        self.opt_criterio = ctk.CTkOptionMenu(
            inner, variable=self._criterio_var,
            values=[c[1] for c in self.CRITERIOS],
            width=170, height=34, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.COLOR_ENTRY_BG, button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            dropdown_fg_color=self.COLOR_PANEL, dropdown_hover_color=self.COLOR_ENTRY_BG,
            text_color=self.COLOR_TEXT,
            command=self._on_criterio_cambiado,
        )
        self.opt_criterio.pack(side="left", padx=(0, 8))

        self.entry_busqueda = ctk.CTkEntry(
            inner, placeholder_text="Ingrese el valor a buscar...",
            height=34, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.COLOR_ENTRY_BG, border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT, placeholder_text_color=self.COLOR_TEXT_SEC,
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_busqueda.bind("<Return>", lambda _: self._ejecutar_busqueda())

        ctk.CTkButton(
            inner, text="Buscar", width=90, height=34, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=self.COLOR_ACCENT, hover_color=self.COLOR_ACCENT_HOVER,
            text_color="#FFF", command=self._ejecutar_busqueda,
        ).pack(side="left")

        # -- Mensaje + conteo --
        info_bar = ctk.CTkFrame(self, fg_color="transparent")
        info_bar.pack(fill="x", pady=(0, 4))

        self.label_mensaje = ctk.CTkLabel(
            info_bar, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_ERROR, anchor="w",
        )
        self.label_mensaje.pack(side="left", padx=4)

        self.label_conteo = ctk.CTkLabel(
            info_bar, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_TEXT_SEC, anchor="e",
        )
        self.label_conteo.pack(side="right", padx=4)

        # -- Tabla --
        tabla_frame = ctk.CTkFrame(self, fg_color=self.COLOR_PANEL, corner_radius=12,
                                   border_width=1, border_color=self.COLOR_ENTRY_BORDER)
        tabla_frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(tabla_frame, fg_color=self.COLOR_ENTRY_BG,
                              corner_radius=0, height=36)
        header.pack(fill="x", padx=4, pady=(4, 0))
        header.pack_propagate(False)
        for i, col in enumerate(self.COLUMNAS):
            header.grid_columnconfigure(i, weight=col["peso"], minsize=col["min"])
            ctk.CTkLabel(header, text=col["texto"],
                         font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                         text_color=self.COLOR_TEXT, anchor="w",
                         ).grid(row=0, column=i, sticky="ew", padx=8, pady=8)

        # Body
        self.scroll = ctk.CTkScrollableFrame(tabla_frame, fg_color="transparent",
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ACCENT)
        self.scroll.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        for i, col in enumerate(self.COLUMNAS):
            self.scroll.grid_columnconfigure(i, weight=col["peso"], minsize=col["min"])

    # ==========================================================================
    #  LOGICA
    # ==========================================================================

    def _on_criterio_cambiado(self, valor):
        if valor == "Todos":
            self.entry_busqueda.delete(0, "end")
            self._ejecutar_busqueda()

    def _cargar_datos(self):
        try:
            registros = self.controller.obtener_todos()
            self._mostrar_resultados(registros)
        except Exception as e:
            self.label_mensaje.configure(text=f"Error: {e}", text_color=self.COLOR_ERROR)

    def _ejecutar_busqueda(self):
        texto_criterio = self._criterio_var.get()
        clave = self._clave_de_texto(texto_criterio)
        valor = self.entry_busqueda.get().strip()

        exito, resultado = self.controller.buscar(clave, valor)
        if exito:
            self._mostrar_resultados(resultado)
            self.label_mensaje.configure(text="")
        else:
            self.label_mensaje.configure(text=str(resultado), text_color=self.COLOR_ERROR)

    def _mostrar_resultados(self, registros):
        for w in self._filas:
            w.destroy()
        self._filas.clear()

        total = len(registros)
        txt = f"{total} resultado{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        self.label_conteo.configure(text=txt)

        if not registros:
            ph = ctk.CTkFrame(self.scroll, fg_color="transparent")
            ph.grid(row=0, column=0, columnspan=len(self.COLUMNAS), pady=30, sticky="ew")
            ctk.CTkLabel(ph, text="No se encontraron registros.",
                         font=ctk.CTkFont(family="Segoe UI", size=13),
                         text_color=self.COLOR_TEXT_SEC).pack()
            self._filas.append(ph)
            return

        for idx, reg in enumerate(registros):
            bg = self.COLOR_ROW_ALT if idx % 2 == 0 else "transparent"
            fila = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=4, height=36)
            fila.grid(row=idx, column=0, columnspan=len(self.COLUMNAS), sticky="ew", pady=1)
            fila.grid_propagate(False)

            for i, col in enumerate(self.COLUMNAS):
                fila.grid_columnconfigure(i, weight=col["peso"], minsize=col["min"])

            nombre = reg.nombre1
            if reg.nombre2:
                nombre += f" {reg.nombre2}"
            nombre += f" {reg.apellido1}"
            if reg.apellido2:
                nombre += f" {reg.apellido2}"

            estado = "Vivo" if reg.estado_vital == 1 else "Fallecido"

            valores = [reg.cedula, nombre, reg.fecha_nacimiento,
                       reg.lugar_nacimiento, estado, reg.num_historia, None]

            for i, val in enumerate(valores):
                if i == 6:  # Color
                    cf = ctk.CTkFrame(fila, fg_color="transparent")
                    cf.grid(row=0, column=i, sticky="ew", padx=6, pady=4)
                    hx = self._hex_color(reg.num_historia)
                    ind = ctk.CTkFrame(cf, fg_color=hx, width=14, height=14, corner_radius=4)
                    ind.pack(side="left", padx=(0, 4))
                    ind.pack_propagate(False)
                    ctk.CTkLabel(cf, text=reg.color or "",
                                 font=ctk.CTkFont(family="Segoe UI", size=11),
                                 text_color=self.COLOR_TEXT, anchor="w").pack(side="left")
                else:
                    ctk.CTkLabel(fila, text=str(val or ""),
                                 font=ctk.CTkFont(family="Segoe UI", size=11),
                                 text_color=self.COLOR_TEXT, anchor="w",
                                 ).grid(row=0, column=i, sticky="ew", padx=8, pady=6)

            self._filas.append(fila)

    # ==========================================================================
    #  UTILIDADES
    # ==========================================================================

    @staticmethod
    def _hex_color(num_historia: str) -> str:
        try:
            d = int(num_historia.split("-")[2][0])
            _, hx = MAPA_COLORES[d]
            return hx
        except (IndexError, ValueError, KeyError):
            return "#666"

    def _clave_de_texto(self, texto: str) -> str:
        for clave, label in self.CRITERIOS:
            if label == texto:
                return clave
        return "todos"
