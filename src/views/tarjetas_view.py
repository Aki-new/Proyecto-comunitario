import customtkinter as ctk

from controllers.tarjeta_controller import TarjetaController
from controllers.paciente_controller import PacienteController
from models.num_historia_utils import (
    obtener_color_por_num_historia,
    validar_formato_num_historia,
)


class TarjetasView(ctk.CTkFrame):
    """Modulo de gestion de tarjetas de salud.

    Se integra como widget hijo dentro del area de contenido del dashboard.
    Implementa CRUD completo con vista previa de color en tiempo real.
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
    COLOR_DANGER = "#FF4C6A"
    COLOR_DANGER_HOVER = "#D93A5A"
    COLOR_ROW_ALT = "#1A2D3D"
    COLOR_SIDEBAR_BORDER = "#1E3044"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        # Controladores
        self.controller = TarjetaController()
        self.pac_controller = PacienteController()

        # Estado interno
        self._tarjeta_seleccionada_id: int | None = None
        self._editando = False
        self._mapa_pacientes: dict[str, int] = {}  # display_text -> id
        self._filas_tabla: list[ctk.CTkFrame] = []

        self._crear_widgets()
        self._cargar_datos()

    # ==========================================================================
    #  LAYOUT PRINCIPAL
    # ==========================================================================

    def _crear_widgets(self):
        """Construye toda la interfaz: toolbar, tabla y formulario."""
        self._crear_toolbar()
        self._crear_cuerpo()

    # -- Barra de herramientas -------------------------------------------------

    def _crear_toolbar(self):
        toolbar = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_PANEL,
            corner_radius=12,
            border_width=1,
            border_color=self.COLOR_SIDEBAR_BORDER,
            height=50,
        )
        toolbar.pack(fill="x", pady=(0, 10))
        toolbar.pack_propagate(False)

        contenedor = ctk.CTkFrame(toolbar, fg_color="transparent")
        contenedor.pack(fill="x", padx=16, pady=8)

        # -- Botones --
        self.btn_nueva = ctk.CTkButton(
            contenedor,
            text="Nueva Tarjeta",
            width=130,
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            command=self._accion_nueva,
        )
        self.btn_nueva.pack(side="left", padx=(0, 6))

        self.btn_guardar = ctk.CTkButton(
            contenedor,
            text="Guardar",
            width=100,
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=self.COLOR_SUCCESS,
            hover_color="#00B377",
            text_color="#FFFFFF",
            command=self._accion_guardar,
        )
        self.btn_guardar.pack(side="left", padx=(0, 6))

        self.btn_eliminar = ctk.CTkButton(
            contenedor,
            text="Eliminar",
            width=100,
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=self.COLOR_DANGER,
            hover_color=self.COLOR_DANGER_HOVER,
            text_color="#FFFFFF",
            command=self._accion_eliminar,
        )
        self.btn_eliminar.pack(side="left", padx=(0, 6))

        self.btn_limpiar = ctk.CTkButton(
            contenedor,
            text="Limpiar",
            width=100,
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.COLOR_ENTRY_BG,
            hover_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_SEC,
            command=self._limpiar_formulario,
        )
        self.btn_limpiar.pack(side="left")

    # -- Cuerpo (tabla + formulario) -------------------------------------------

    def _crear_cuerpo(self):
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=65)
        cuerpo.grid_columnconfigure(1, weight=35)
        cuerpo.grid_rowconfigure(0, weight=1)

        self._crear_tabla(cuerpo)
        self._crear_formulario(cuerpo)

    # ==========================================================================
    #  TABLA
    # ==========================================================================

    def _crear_tabla(self, parent):
        panel_tabla = ctk.CTkFrame(
            parent,
            fg_color=self.COLOR_PANEL,
            corner_radius=12,
            border_width=1,
            border_color=self.COLOR_SIDEBAR_BORDER,
        )
        panel_tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Titulo
        ctk.CTkLabel(
            panel_tabla,
            text="Tarjetas Registradas",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 8))

        # -- Encabezado --
        header = ctk.CTkFrame(panel_tabla, fg_color=self.COLOR_ENTRY_BG, corner_radius=6, height=36)
        header.pack(fill="x", padx=12, pady=(0, 4))
        header.pack_propagate(False)

        columnas = [
            ("N. Historia", 0.20),
            ("Paciente", 0.30),
            ("Cedula", 0.20),
            ("Color", 0.30),
        ]
        for texto, peso in columnas:
            ctk.CTkLabel(
                header,
                text=texto,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=self.COLOR_TEXT_SEC,
                anchor="w",
            ).pack(side="left", padx=10, expand=True, fill="x")

        # -- Contenedor scrollable --
        self.scroll_tabla = ctk.CTkScrollableFrame(
            panel_tabla,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ENTRY_BORDER,
        )
        self.scroll_tabla.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # -- Llenar filas de la tabla ----------------------------------------------

    def _llenar_tabla(self, tarjetas):
        """Limpia y reconstruye las filas de la tabla con los datos actuales."""
        # Destruir filas previas
        for fila in self._filas_tabla:
            fila.destroy()
        self._filas_tabla.clear()

        for idx, tarjeta in enumerate(tarjetas):
            color_fila = self.COLOR_ROW_ALT if idx % 2 == 0 else self.COLOR_PANEL

            fila = ctk.CTkFrame(
                self.scroll_tabla,
                fg_color=color_fila,
                corner_radius=6,
                height=38,
            )
            fila.pack(fill="x", pady=1)
            fila.pack_propagate(False)

            # -- N. Historia --
            ctk.CTkLabel(
                fila,
                text=tarjeta.num_historia,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=self.COLOR_TEXT,
                anchor="w",
            ).pack(side="left", padx=10, expand=True, fill="x")

            # -- Paciente (nombre1 apellido1) --
            nombre_paciente = self._obtener_nombre_paciente(tarjeta.id_paciente)
            ctk.CTkLabel(
                fila,
                text=nombre_paciente,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=self.COLOR_TEXT,
                anchor="w",
            ).pack(side="left", padx=10, expand=True, fill="x")

            # -- Cedula --
            cedula_paciente = self._obtener_cedula_paciente(tarjeta.id_paciente)
            ctk.CTkLabel(
                fila,
                text=cedula_paciente,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=self.COLOR_TEXT,
                anchor="w",
            ).pack(side="left", padx=10, expand=True, fill="x")

            # -- Color (cuadro de color + nombre) --
            color_frame = ctk.CTkFrame(fila, fg_color="transparent")
            color_frame.pack(side="left", padx=10, expand=True, fill="x")

            try:
                info_color = obtener_color_por_num_historia(tarjeta.num_historia)
                color_hex = info_color["hex"]
                color_nombre = info_color["nombre"]
            except (ValueError, KeyError):
                color_hex = "#555555"
                color_nombre = "Desconocido"

            cuadro = ctk.CTkFrame(
                color_frame,
                fg_color=color_hex,
                corner_radius=4,
                width=16,
                height=16,
            )
            cuadro.pack(side="left", padx=(0, 6))
            cuadro.pack_propagate(False)

            ctk.CTkLabel(
                color_frame,
                text=color_nombre,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=self.COLOR_TEXT,
                anchor="w",
            ).pack(side="left")

            # Bind click en toda la fila
            self._bind_fila(fila, tarjeta)

            self._filas_tabla.append(fila)

    def _bind_fila(self, fila: ctk.CTkFrame, tarjeta):
        """Vincula el click en la fila para seleccionar la tarjeta."""
        def on_click(event, t=tarjeta):
            self._seleccionar_tarjeta(t)

        fila.bind("<Button-1>", on_click)
        # Tambien los hijos
        for child in fila.winfo_children():
            child.bind("<Button-1>", on_click)
            # Hijos anidados (color_frame)
            if hasattr(child, "winfo_children"):
                for subchild in child.winfo_children():
                    subchild.bind("<Button-1>", on_click)

    # ==========================================================================
    #  FORMULARIO
    # ==========================================================================

    def _crear_formulario(self, parent):
        panel_form = ctk.CTkFrame(
            parent,
            fg_color=self.COLOR_PANEL,
            corner_radius=12,
            border_width=1,
            border_color=self.COLOR_SIDEBAR_BORDER,
        )
        panel_form.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Titulo del formulario
        ctk.CTkLabel(
            panel_form,
            text="Datos de la Tarjeta",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 12))

        # -- Paciente (OptionMenu) --
        ctk.CTkLabel(
            panel_form,
            text="Paciente",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 4))

        self.option_paciente = ctk.CTkOptionMenu(
            panel_form,
            values=["-- Seleccione --"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=self.COLOR_ENTRY_BG,
            button_color=self.COLOR_ENTRY_BORDER,
            button_hover_color=self.COLOR_ACCENT,
            dropdown_fg_color=self.COLOR_PANEL,
            dropdown_hover_color=self.COLOR_ENTRY_BG,
            text_color=self.COLOR_TEXT,
            dropdown_text_color=self.COLOR_TEXT,
            corner_radius=8,
            height=36,
        )
        self.option_paciente.pack(fill="x", padx=16, pady=(0, 10))

        # -- Numero de Historia --
        ctk.CTkLabel(
            panel_form,
            text="Numero de Historia",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 4))

        self.entry_num_historia = ctk.CTkEntry(
            panel_form,
            placeholder_text="XX-XX-XX",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=self.COLOR_ENTRY_BG,
            border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT,
            placeholder_text_color=self.COLOR_TEXT_SEC,
            corner_radius=8,
            height=36,
        )
        self.entry_num_historia.pack(fill="x", padx=16, pady=(0, 10))

        # Bind para vista previa en tiempo real
        self.entry_num_historia.bind("<KeyRelease>", self._on_num_historia_change)

        # -- Vista previa de color (LIVE PREVIEW) --
        ctk.CTkLabel(
            panel_form,
            text="Color Asignado",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 4))

        preview_frame = ctk.CTkFrame(
            panel_form,
            fg_color=self.COLOR_ENTRY_BG,
            corner_radius=8,
            height=44,
        )
        preview_frame.pack(fill="x", padx=16, pady=(0, 10))
        preview_frame.pack_propagate(False)

        contenedor_preview = ctk.CTkFrame(preview_frame, fg_color="transparent")
        contenedor_preview.pack(fill="both", expand=True, padx=12)

        self.preview_cuadro = ctk.CTkFrame(
            contenedor_preview,
            fg_color="#555555",
            corner_radius=6,
            width=28,
            height=28,
        )
        self.preview_cuadro.pack(side="left", padx=(0, 10), pady=8)
        self.preview_cuadro.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            contenedor_preview,
            text="Ingrese un numero de historia",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
        )
        self.preview_label.pack(side="left", fill="x", expand=True)

        # -- Mensaje de retroalimentacion --
        self.label_mensaje = ctk.CTkLabel(
            panel_form,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_TEXT_SEC,
            anchor="w",
            wraplength=280,
        )
        self.label_mensaje.pack(fill="x", padx=16, pady=(6, 10))

    # ==========================================================================
    #  CARGA DE DATOS
    # ==========================================================================

    def _cargar_datos(self):
        """Carga tarjetas en la tabla y pacientes en el dropdown."""
        try:
            tarjetas = self.controller.listar_tarjetas()
            self._llenar_tabla(tarjetas)
        except Exception as e:
            self._mostrar_mensaje(f"Error al cargar tarjetas: {e}", error=True)

        self._cargar_pacientes_dropdown()

    def _cargar_pacientes_dropdown(self, incluir_id: int | None = None):
        """Carga el dropdown con pacientes disponibles (sin tarjeta activa).

        Args:
            incluir_id: Si se esta editando, incluir al paciente actual
                        aunque ya tenga tarjeta.
        """
        try:
            pacientes = self.pac_controller.listar_pacientes()
            tarjetas = self.controller.listar_tarjetas()
        except Exception as e:
            self._mostrar_mensaje(f"Error al cargar pacientes: {e}", error=True)
            return

        # IDs de pacientes que ya tienen tarjeta
        ids_con_tarjeta = {t.id_paciente for t in tarjetas}

        self._mapa_pacientes.clear()
        opciones = []

        for pac in pacientes:
            # Solo mostrar los que no tienen tarjeta, excepto el actual si editamos
            if pac.id not in ids_con_tarjeta or pac.id == incluir_id:
                display = f"{pac.cedula} - {pac.nombre1} {pac.apellido1}"
                self._mapa_pacientes[display] = pac.id
                opciones.append(display)

        if not opciones:
            opciones = ["-- Sin pacientes disponibles --"]

        self.option_paciente.configure(values=opciones)
        self.option_paciente.set(opciones[0] if opciones else "-- Seleccione --")

    # -- Helpers para obtener datos de paciente --------------------------------

    def _obtener_nombre_paciente(self, id_paciente: int) -> str:
        """Retorna 'nombre1 apellido1' del paciente, o su ID si falla."""
        try:
            ok, resultado = self.pac_controller.obtener_paciente(id_paciente)
            if ok:
                return f"{resultado.nombre1} {resultado.apellido1}"
        except Exception:
            pass
        return f"ID: {id_paciente}"

    def _obtener_cedula_paciente(self, id_paciente: int) -> str:
        """Retorna la cedula del paciente, o 'N/A' si falla."""
        try:
            ok, resultado = self.pac_controller.obtener_paciente(id_paciente)
            if ok:
                return resultado.cedula
        except Exception:
            pass
        return "N/A"

    # ==========================================================================
    #  VISTA PREVIA EN TIEMPO REAL
    # ==========================================================================

    def _on_num_historia_change(self, event=None):
        """Actualiza la vista previa del color mientras el usuario escribe."""
        valor = self.entry_num_historia.get().strip()

        if not valor:
            self.preview_cuadro.configure(fg_color="#555555")
            self.preview_label.configure(
                text="Ingrese un numero de historia",
                text_color=self.COLOR_TEXT_SEC,
            )
            return

        if validar_formato_num_historia(valor):
            try:
                info = obtener_color_por_num_historia(valor)
                self.preview_cuadro.configure(fg_color=info["hex"])
                self.preview_label.configure(
                    text=f"{info['nombre']}  ({info['hex']})",
                    text_color=self.COLOR_TEXT,
                )
            except (ValueError, KeyError):
                self.preview_cuadro.configure(fg_color="#555555")
                self.preview_label.configure(
                    text="Error al determinar color",
                    text_color=self.COLOR_ERROR,
                )
        else:
            self.preview_cuadro.configure(fg_color="#555555")
            self.preview_label.configure(
                text="Formato: XX-XX-XX (ej: 03-77-34)",
                text_color=self.COLOR_TEXT_SEC,
            )

    # ==========================================================================
    #  SELECCION DE FILA
    # ==========================================================================

    def _seleccionar_tarjeta(self, tarjeta):
        """Puebla el formulario con los datos de la tarjeta seleccionada."""
        self._tarjeta_seleccionada_id = tarjeta.id
        self._editando = True

        # Cargar dropdown incluyendo el paciente actual
        self._cargar_pacientes_dropdown(incluir_id=tarjeta.id_paciente)

        # Seleccionar el paciente en el dropdown
        for display, pid in self._mapa_pacientes.items():
            if pid == tarjeta.id_paciente:
                self.option_paciente.set(display)
                break

        # Deshabilitar el selector de paciente al editar
        self.option_paciente.configure(state="disabled")

        # Llenar num_historia
        self.entry_num_historia.delete(0, "end")
        self.entry_num_historia.insert(0, tarjeta.num_historia)

        # Disparar preview
        self._on_num_historia_change()

        self._mostrar_mensaje(
            f"Tarjeta seleccionada (ID: {tarjeta.id}). Modifique y presione Guardar.",
            error=False,
        )

    # ==========================================================================
    #  ACCIONES
    # ==========================================================================

    def _accion_nueva(self):
        """Prepara el formulario para crear una nueva tarjeta."""
        self._limpiar_formulario()
        self._mostrar_mensaje("Complete los datos y presione Guardar.", error=False)

    def _accion_guardar(self):
        """Crea o actualiza una tarjeta segun el estado del formulario."""
        num_historia = self.entry_num_historia.get().strip()

        if not num_historia:
            self._mostrar_mensaje("Debe ingresar un numero de historia.", error=True)
            return

        if self._editando and self._tarjeta_seleccionada_id is not None:
            # -- ACTUALIZAR --
            ok, msg = self.controller.actualizar_tarjeta(
                self._tarjeta_seleccionada_id, num_historia
            )
        else:
            # -- CREAR --
            seleccion = self.option_paciente.get()
            if seleccion not in self._mapa_pacientes:
                self._mostrar_mensaje("Debe seleccionar un paciente valido.", error=True)
                return

            id_paciente = self._mapa_pacientes[seleccion]
            ok, msg = self.controller.crear_tarjeta(id_paciente, num_historia)

        self._mostrar_mensaje(msg, error=not ok)

        if ok:
            self._limpiar_formulario()
            self._cargar_datos()

    def _accion_eliminar(self):
        """Desactiva la tarjeta seleccionada (borrado logico)."""
        if self._tarjeta_seleccionada_id is None:
            self._mostrar_mensaje(
                "Seleccione una tarjeta de la tabla para eliminar.", error=True
            )
            return

        ok, msg = self.controller.eliminar_tarjeta(self._tarjeta_seleccionada_id)
        self._mostrar_mensaje(msg, error=not ok)

        if ok:
            self._limpiar_formulario()
            self._cargar_datos()

    # ==========================================================================
    #  UTILIDADES
    # ==========================================================================

    def _limpiar_formulario(self):
        """Resetea el formulario a su estado inicial."""
        self._tarjeta_seleccionada_id = None
        self._editando = False

        self.entry_num_historia.delete(0, "end")
        self.option_paciente.configure(state="normal")
        self._cargar_pacientes_dropdown()

        # Resetear preview
        self.preview_cuadro.configure(fg_color="#555555")
        self.preview_label.configure(
            text="Ingrese un numero de historia",
            text_color=self.COLOR_TEXT_SEC,
        )

        self.label_mensaje.configure(text="", text_color=self.COLOR_TEXT_SEC)

    def _mostrar_mensaje(self, texto: str, error: bool = False):
        """Muestra un mensaje de retroalimentacion en el formulario."""
        color = self.COLOR_ERROR if error else self.COLOR_SUCCESS
        self.label_mensaje.configure(text=texto, text_color=color)
