import customtkinter as ctk
from controllers.usuario_controller import UsuarioController


class UsuariosView(ctk.CTkFrame):
    """Modulo de gestion de usuarios con CRUD completo.
    Permite listar, crear, actualizar y eliminar usuarios del sistema.
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
    COLOR_WARNING = "#FFB800"
    COLOR_DANGER = "#FF4C6A"
    COLOR_DANGER_HOVER = "#D93A5A"
    COLOR_ROW_ALT = "#1A2D3D"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = UsuarioController()
        self._usuario_seleccionado = None
        self._filas_widgets: list[ctk.CTkFrame] = []
        self._crear_widgets()
        self._cargar_datos()

    # ==========================================================================
    # Construccion de la interfaz
    # ==========================================================================

    def _crear_widgets(self):
        """Construye la barra de herramientas, la tabla y el formulario."""

        # -- Barra de herramientas ---------------------------------------------
        self._crear_toolbar()

        # -- Mensaje de retroalimentacion --------------------------------------
        self.label_mensaje = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.COLOR_SUCCESS,
            anchor="w",
        )
        self.label_mensaje.pack(fill="x", padx=4, pady=(0, 6))

        # -- Contenedor principal (tabla + formulario) -------------------------
        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.pack(fill="both", expand=True)
        contenedor.grid_columnconfigure(0, weight=65)
        contenedor.grid_columnconfigure(1, weight=35)
        contenedor.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: tabla
        self._crear_tabla(contenedor)

        # Panel derecho: formulario
        self._crear_formulario(contenedor)

    # --------------------------------------------------------------------------
    # Toolbar
    # --------------------------------------------------------------------------

    def _crear_toolbar(self):
        """Barra superior con botones de accion."""
        toolbar = ctk.CTkFrame(
            self, fg_color=self.COLOR_PANEL,
            corner_radius=12, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )
        toolbar.pack(fill="x", pady=(0, 10))

        contenedor = ctk.CTkFrame(toolbar, fg_color="transparent")
        contenedor.pack(fill="x", padx=12, pady=10)

        btn_config = {
            "height": 34, "corner_radius": 8,
            "font": ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        }

        self.btn_nuevo = ctk.CTkButton(
            contenedor, text="Nuevo",
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            command=self._accion_nuevo,
            **btn_config,
        )
        self.btn_nuevo.pack(side="left", padx=(0, 6))

        self.btn_guardar = ctk.CTkButton(
            contenedor, text="Guardar",
            fg_color=self.COLOR_SUCCESS,
            hover_color="#00B377",
            text_color="#FFFFFF",
            command=self._accion_guardar,
            **btn_config,
        )
        self.btn_guardar.pack(side="left", padx=(0, 6))

        self.btn_eliminar = ctk.CTkButton(
            contenedor, text="Eliminar",
            fg_color=self.COLOR_DANGER,
            hover_color=self.COLOR_DANGER_HOVER,
            text_color="#FFFFFF",
            command=self._accion_eliminar,
            **btn_config,
        )
        self.btn_eliminar.pack(side="left", padx=(0, 6))

        self.btn_limpiar = ctk.CTkButton(
            contenedor, text="Limpiar",
            fg_color=self.COLOR_ENTRY_BG,
            hover_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT,
            command=self._accion_limpiar,
            **btn_config,
        )
        self.btn_limpiar.pack(side="left")

    # --------------------------------------------------------------------------
    # Tabla (panel izquierdo)
    # --------------------------------------------------------------------------

    def _crear_tabla(self, parent):
        """Tabla de usuarios con scroll."""
        tabla_panel = ctk.CTkFrame(
            parent, fg_color=self.COLOR_PANEL,
            corner_radius=12, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )
        tabla_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Titulo del panel
        ctk.CTkLabel(
            tabla_panel,
            text="Usuarios Registrados",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 6))

        # Cabecera
        self._crear_cabecera_tabla(tabla_panel)

        # Area de scroll para las filas
        self.scroll_tabla = ctk.CTkScrollableFrame(
            tabla_panel, fg_color="transparent",
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ACCENT,
        )
        self.scroll_tabla.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        for i, peso in enumerate(self._col_pesos()):
            self.scroll_tabla.grid_columnconfigure(i, weight=peso)

    @staticmethod
    def _col_nombres():
        return ["Cedula", "Nombre Completo", "Usuario"]

    @staticmethod
    def _col_pesos():
        return [1, 2, 1]

    def _crear_cabecera_tabla(self, parent):
        """Dibuja la fila de cabecera."""
        header = ctk.CTkFrame(parent, fg_color=self.COLOR_ENTRY_BG, height=36, corner_radius=0)
        header.pack(fill="x", padx=4, pady=(0, 0))
        header.pack_propagate(False)

        for i, (nombre, peso) in enumerate(
            zip(self._col_nombres(), self._col_pesos())
        ):
            header.grid_columnconfigure(i, weight=peso)
            ctk.CTkLabel(
                header, text=nombre,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=self.COLOR_TEXT,
                anchor="w",
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=6)

    # --------------------------------------------------------------------------
    # Formulario (panel derecho)
    # --------------------------------------------------------------------------

    def _crear_formulario(self, parent):
        """Panel de formulario para crear/editar usuarios."""
        form_panel = ctk.CTkFrame(
            parent, fg_color=self.COLOR_PANEL,
            corner_radius=12, border_width=1,
            border_color=self.COLOR_ENTRY_BORDER,
        )
        form_panel.grid(row=0, column=1, sticky="nsew")

        # Titulo
        ctk.CTkLabel(
            form_panel,
            text="Datos del Usuario",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(16, 12))

        # Separador
        ctk.CTkFrame(
            form_panel, fg_color=self.COLOR_ENTRY_BORDER, height=1,
        ).pack(fill="x", padx=16, pady=(0, 12))

        # Contenedor de campos
        campos_frame = ctk.CTkFrame(form_panel, fg_color="transparent")
        campos_frame.pack(fill="x", padx=16)

        entry_cfg = {
            "height": 38, "corner_radius": 8,
            "font": ctk.CTkFont(family="Segoe UI", size=13),
            "fg_color": self.COLOR_ENTRY_BG,
            "border_color": self.COLOR_ENTRY_BORDER,
            "text_color": self.COLOR_TEXT,
            "placeholder_text_color": self.COLOR_TEXT_SEC,
        }

        label_cfg = {
            "font": ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            "text_color": self.COLOR_TEXT_SEC,
            "anchor": "w",
        }

        # Nombre
        ctk.CTkLabel(campos_frame, text="Nombre", **label_cfg).pack(
            fill="x", pady=(0, 4))
        self.entry_nombre = ctk.CTkEntry(
            campos_frame, placeholder_text="Nombre del usuario", **entry_cfg)
        self.entry_nombre.pack(fill="x", pady=(0, 10))

        # Apellido
        ctk.CTkLabel(campos_frame, text="Apellido", **label_cfg).pack(
            fill="x", pady=(0, 4))
        self.entry_apellido = ctk.CTkEntry(
            campos_frame, placeholder_text="Apellido del usuario", **entry_cfg)
        self.entry_apellido.pack(fill="x", pady=(0, 10))

        # Cedula
        ctk.CTkLabel(campos_frame, text="Cedula", **label_cfg).pack(
            fill="x", pady=(0, 4))
        self.entry_cedula = ctk.CTkEntry(
            campos_frame, placeholder_text="Cedula (solo numeros)", **entry_cfg)
        self.entry_cedula.pack(fill="x", pady=(0, 10))

        # Usuario
        ctk.CTkLabel(campos_frame, text="Usuario", **label_cfg).pack(
            fill="x", pady=(0, 4))
        self.entry_usuario = ctk.CTkEntry(
            campos_frame, placeholder_text="Nombre de usuario", **entry_cfg)
        self.entry_usuario.pack(fill="x", pady=(0, 10))

        # Clave
        ctk.CTkLabel(campos_frame, text="Clave", **label_cfg).pack(
            fill="x", pady=(0, 4))
        self.entry_clave = ctk.CTkEntry(
            campos_frame, placeholder_text="Clave de acceso",
            show="*", **entry_cfg)
        self.entry_clave.pack(fill="x", pady=(0, 10))

        # Label de validacion del formulario
        self.label_form_error = ctk.CTkLabel(
            form_panel, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_ERROR,
            anchor="w",
            wraplength=280,
        )
        self.label_form_error.pack(fill="x", padx=16, pady=(4, 4))

    # ==========================================================================
    # Carga de datos
    # ==========================================================================

    def _cargar_datos(self):
        """Carga la lista de usuarios desde el controlador."""
        try:
            usuarios = self.controller.listar_usuarios()
            self._renderizar_tabla(usuarios)
        except Exception as e:
            self._mostrar_mensaje(f"Error al cargar usuarios: {e}", error=True)

    def _renderizar_tabla(self, usuarios):
        """Limpia y redibuja las filas de la tabla."""
        for widget in self._filas_widgets:
            widget.destroy()
        self._filas_widgets.clear()

        if not usuarios:
            placeholder = ctk.CTkFrame(self.scroll_tabla, fg_color="transparent")
            placeholder.grid(row=0, column=0, columnspan=3, pady=40, sticky="ew")
            ctk.CTkLabel(
                placeholder,
                text="No hay usuarios registrados.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=self.COLOR_TEXT_SEC,
            ).pack()
            self._filas_widgets.append(placeholder)
            return

        for idx, usuario in enumerate(usuarios):
            bg = self.COLOR_ROW_ALT if idx % 2 == 0 else "transparent"
            fila = ctk.CTkFrame(
                self.scroll_tabla, fg_color=bg,
                height=36, corner_radius=0,
            )
            fila.grid(row=idx, column=0, columnspan=3, sticky="ew")
            fila.grid_propagate(False)

            for j, peso in enumerate(self._col_pesos()):
                fila.grid_columnconfigure(j, weight=peso)

            nombre_completo = f"{usuario.nombre} {usuario.apellido}"

            valores = [
                str(usuario.cedula),
                nombre_completo,
                usuario.usuario,
            ]

            for j, val in enumerate(valores):
                ctk.CTkLabel(
                    fila, text=val,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=self.COLOR_TEXT,
                    anchor="w",
                ).grid(row=0, column=j, sticky="ew", padx=10, pady=6)

            # Bind click para seleccionar fila
            fila.bind("<Button-1>", lambda e, u=usuario: self._seleccionar_usuario(u))
            for child in fila.winfo_children():
                child.bind("<Button-1>", lambda e, u=usuario: self._seleccionar_usuario(u))

            self._filas_widgets.append(fila)

    # ==========================================================================
    # Seleccion y llenado del formulario
    # ==========================================================================

    def _seleccionar_usuario(self, usuario):
        """Carga los datos del usuario seleccionado en el formulario."""
        self._usuario_seleccionado = usuario
        self.label_form_error.configure(text="")

        self._set_entry(self.entry_nombre, usuario.nombre)
        self._set_entry(self.entry_apellido, usuario.apellido)
        self._set_entry(self.entry_cedula, str(usuario.cedula))
        self._set_entry(self.entry_usuario, usuario.usuario)
        self.entry_clave.delete(0, "end")

    @staticmethod
    def _set_entry(entry, valor: str):
        """Limpia y escribe un valor en un CTkEntry."""
        entry.delete(0, "end")
        entry.insert(0, valor)

    # ==========================================================================
    # Acciones CRUD
    # ==========================================================================

    def _accion_nuevo(self):
        """Limpia el formulario para registrar un nuevo usuario."""
        self._usuario_seleccionado = None
        self._limpiar_formulario()
        self._mostrar_mensaje("Complete los campos para registrar un nuevo usuario.", error=False)
        self.entry_nombre.focus_set()

    def _accion_guardar(self):
        """Registra o actualiza un usuario segun el estado del formulario."""
        datos = self._obtener_datos_formulario()
        if datos is None:
            return

        if self._usuario_seleccionado is None:
            # Crear nuevo usuario
            exito, mensaje = self.controller.registrar_usuario(datos)
        else:
            # Actualizar usuario existente
            exito, mensaje = self.controller.actualizar_usuario(
                self._usuario_seleccionado.id, datos
            )

        if exito:
            self._mostrar_mensaje(mensaje, error=False)
            self._limpiar_formulario()
            self._usuario_seleccionado = None
            self._cargar_datos()
        else:
            self._mostrar_mensaje(mensaje, error=True)

    def _accion_eliminar(self):
        """Elimina (desactiva) el usuario seleccionado."""
        if self._usuario_seleccionado is None:
            self._mostrar_mensaje(
                "Seleccione un usuario de la tabla para eliminar.", error=True
            )
            return

        exito, mensaje = self.controller.eliminar_usuario(
            self._usuario_seleccionado.id
        )

        if exito:
            self._mostrar_mensaje(mensaje, error=False)
            self._limpiar_formulario()
            self._usuario_seleccionado = None
            self._cargar_datos()
        else:
            self._mostrar_mensaje(mensaje, error=True)

    def _accion_limpiar(self):
        """Limpia el formulario y la seleccion."""
        self._usuario_seleccionado = None
        self._limpiar_formulario()
        self.label_mensaje.configure(text="")
        self.label_form_error.configure(text="")

    # ==========================================================================
    # Utilidades de formulario
    # ==========================================================================

    def _obtener_datos_formulario(self) -> dict | None:
        """Lee los campos del formulario y valida que no esten vacios.

        Returns:
            Diccionario con los datos o None si hay errores.
        """
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        cedula_txt = self.entry_cedula.get().strip()
        usuario = self.entry_usuario.get().strip()
        clave = self.entry_clave.get().strip()

        # Validar campos obligatorios
        vacios = []
        if not nombre:
            vacios.append("Nombre")
        if not apellido:
            vacios.append("Apellido")
        if not cedula_txt:
            vacios.append("Cedula")
        if not usuario:
            vacios.append("Usuario")
        if not clave:
            vacios.append("Clave")

        if vacios:
            self.label_form_error.configure(
                text=f"Campos requeridos: {', '.join(vacios)}",
                text_color=self.COLOR_ERROR,
            )
            return None

        # Validar cedula numerica
        try:
            cedula = int(cedula_txt)
        except ValueError:
            self.label_form_error.configure(
                text="La cedula debe contener solo numeros.",
                text_color=self.COLOR_ERROR,
            )
            return None

        self.label_form_error.configure(text="")

        return {
            "nombre": nombre,
            "apellido": apellido,
            "cedula": cedula,
            "usuario": usuario,
            "clave": clave,
        }

    def _limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.entry_nombre.delete(0, "end")
        self.entry_apellido.delete(0, "end")
        self.entry_cedula.delete(0, "end")
        self.entry_usuario.delete(0, "end")
        self.entry_clave.delete(0, "end")
        self.label_form_error.configure(text="")

    def _mostrar_mensaje(self, mensaje: str, error: bool = False):
        """Muestra un mensaje en el label de retroalimentacion."""
        color = self.COLOR_ERROR if error else self.COLOR_SUCCESS
        self.label_mensaje.configure(text=mensaje, text_color=color)
