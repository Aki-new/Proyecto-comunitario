import customtkinter as ctk
from controllers.paciente_controller import PacienteController
from controllers.tarjeta_controller import TarjetaController
from controllers.busqueda_controller import BusquedaController
from models.num_historia_utils import (
    obtener_color_por_num_historia,
    validar_formato_num_historia,
    MAPA_COLORES,
)


class PacientesView(ctk.CTkFrame):
    """Modulo unificado: busqueda + registro de paciente con tarjeta indice."""

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

    CRITERIOS = [
        ("todos",            "Todos"),
        ("cedula",           "Cedula"),
        ("nombre_completo",  "Nombre Completo"),
        ("apellido",         "Apellido"),
        ("fecha_nacimiento", "Fecha Nacimiento"),
        ("lugar_nacimiento", "Lugar Nacimiento"),
    ]

    # Anchos fijos en pixeles para alineacion perfecta
    COL_WIDTHS = [90, 180, 85, 110, 80, 100]
    COL_NAMES = ["Cedula", "Nombre", "F. Nac.", "Lugar Nac.", "N. Historia", "Color"]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.pac_ctrl = PacienteController()
        self.tarj_ctrl = TarjetaController()
        self.busq_ctrl = BusquedaController()
        self.id_pac_sel: int | None = None
        self.id_tarj_sel: int | None = None
        self._filas: list[ctk.CTkFrame] = []
        self._form_visible = False
        self._crear_ui()
        self._buscar_todo()

    # ==========================================================================
    #  UI
    # ==========================================================================

    def _crear_ui(self):
        # ── Barra busqueda (compacta, altura fija) ──
        barra = ctk.CTkFrame(self, fg_color=self.COLOR_PANEL, corner_radius=8,
                             height=42)
        barra.pack(fill="x", pady=(0, 3))
        barra.pack_propagate(False)

        ctk.CTkLabel(barra, text="Buscar:",
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color=self.COLOR_TEXT_SEC,
                     ).pack(side="left", padx=(10, 4))

        self._crit_var = ctk.StringVar(value="Todos")
        ctk.CTkOptionMenu(
            barra, variable=self._crit_var,
            values=[c[1] for c in self.CRITERIOS],
            width=145, height=26, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=self.COLOR_ENTRY_BG, button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            dropdown_fg_color=self.COLOR_PANEL, dropdown_hover_color=self.COLOR_ENTRY_BG,
            text_color=self.COLOR_TEXT, command=self._on_crit,
        ).pack(side="left", padx=(0, 4))

        self.entry_busq = ctk.CTkEntry(
            barra, placeholder_text="Ingrese valor de busqueda...",
            height=26, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=self.COLOR_ENTRY_BG, border_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT, placeholder_text_color=self.COLOR_TEXT_SEC,
        )
        self.entry_busq.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.entry_busq.bind("<Return>", lambda _: self._buscar())

        b = dict(height=26, corner_radius=6,
                 font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))

        ctk.CTkButton(barra, text="Buscar", width=65,
                      fg_color=self.COLOR_ACCENT, hover_color=self.COLOR_ACCENT_HOVER,
                      text_color="#FFF", command=self._buscar, **b,
                      ).pack(side="left", padx=(0, 8))

        ctk.CTkFrame(barra, fg_color=self.COLOR_ENTRY_BORDER, width=1
                     ).pack(side="left", fill="y", pady=8, padx=(0, 8))

        ctk.CTkButton(barra, text="+ Nuevo Ingreso", width=120,
                      fg_color=self.COLOR_SUCCESS, hover_color="#00B377",
                      text_color="#FFF", command=self._nuevo, **b,
                      ).pack(side="left", padx=(0, 10))

        # ── Info (conteo + mensaje) ──
        info = ctk.CTkFrame(self, fg_color="transparent", height=18)
        info.pack(fill="x", pady=(0, 2))
        info.pack_propagate(False)

        self.lbl_msg = ctk.CTkLabel(info, text="", anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=10), text_color=self.COLOR_TEXT_SEC)
        self.lbl_msg.pack(side="left", padx=4)

        self.lbl_cnt = ctk.CTkLabel(info, text="", anchor="e",
            font=ctk.CTkFont(family="Segoe UI", size=10), text_color=self.COLOR_TEXT_SEC)
        self.lbl_cnt.pack(side="right", padx=4)

        # ── Cuerpo ──
        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.pack(fill="both", expand=True)
        self.cuerpo.grid_columnconfigure(0, weight=1)
        self.cuerpo.grid_rowconfigure(0, weight=1)

        self._crear_tabla(self.cuerpo)
        self._crear_form(self.cuerpo)

    # -- Tabla (header + datos en el MISMO scroll = alineacion perfecta) -------
    def _crear_tabla(self, parent):
        self.p_tabla = ctk.CTkFrame(parent, fg_color=self.COLOR_PANEL,
                                     corner_radius=8, border_width=1,
                                     border_color=self.COLOR_ENTRY_BORDER)
        self.p_tabla.grid(row=0, column=0, sticky="nsew")
        self.p_tabla.grid_rowconfigure(0, weight=1)
        self.p_tabla.grid_columnconfigure(0, weight=1)

        self.tscroll = ctk.CTkScrollableFrame(
            self.p_tabla, fg_color="transparent",
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ACCENT)
        self.tscroll.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        # Configurar columnas con anchos fijos
        for i, w in enumerate(self.COL_WIDTHS):
            self.tscroll.grid_columnconfigure(i, weight=1, minsize=w)

        # Header DENTRO del scroll (alineacion perfecta garantizada)
        hdr = ctk.CTkFrame(self.tscroll, fg_color=self.COLOR_ENTRY_BG,
                           corner_radius=4, height=28)
        hdr.grid(row=0, column=0, columnspan=len(self.COL_NAMES),
                 sticky="ew", pady=(0, 3))
        hdr.grid_propagate(False)
        for i, (name, w) in enumerate(zip(self.COL_NAMES, self.COL_WIDTHS)):
            hdr.grid_columnconfigure(i, weight=1, minsize=w)
            ctk.CTkLabel(hdr, text=name,
                         font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                         text_color=self.COLOR_TEXT_SEC, anchor="w",
                         ).grid(row=0, column=i, sticky="ew", padx=6, pady=5)

    # -- Formulario ------------------------------------------------------------
    def _crear_form(self, parent):
        self.p_form = ctk.CTkFrame(parent, fg_color=self.COLOR_PANEL,
                                    corner_radius=8, border_width=1,
                                    border_color=self.COLOR_ENTRY_BORDER)

        fh = ctk.CTkFrame(self.p_form, fg_color="transparent")
        fh.pack(fill="x", padx=10, pady=(8, 0))

        self.lbl_ftitle = ctk.CTkLabel(fh, text="Nuevo Ingreso",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.COLOR_TEXT, anchor="w")
        self.lbl_ftitle.pack(side="left")

        ctk.CTkButton(fh, text="X", width=26, height=22, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=self.COLOR_ENTRY_BG, hover_color=self.COLOR_ENTRY_BORDER,
            text_color=self.COLOR_TEXT_SEC, command=self._cerrar_form,
        ).pack(side="right")

        bf = ctk.CTkFrame(self.p_form, fg_color="transparent")
        bf.pack(fill="x", padx=10, pady=(6, 2))

        bb = dict(height=26, corner_radius=6,
                  font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"))

        ctk.CTkButton(bf, text="Guardar", width=70,
                      fg_color=self.COLOR_SUCCESS, hover_color="#00B377",
                      text_color="#FFF", command=self._guardar, **bb,
                      ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(bf, text="Eliminar", width=70,
                      fg_color=self.COLOR_DANGER, hover_color=self.COLOR_DANGER_HOVER,
                      text_color="#FFF", command=self._eliminar, **bb,
                      ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(bf, text="Limpiar", width=60,
                      fg_color=self.COLOR_ENTRY_BG, hover_color=self.COLOR_ENTRY_BORDER,
                      text_color=self.COLOR_TEXT_SEC, command=self._limpiar, **bb,
                      ).pack(side="left")

        ctk.CTkFrame(self.p_form, fg_color=self.COLOR_ENTRY_BORDER, height=1
                     ).pack(fill="x", padx=10, pady=(4, 2))

        fm = ctk.CTkScrollableFrame(self.p_form, fg_color="transparent",
            scrollbar_button_color=self.COLOR_ENTRY_BG,
            scrollbar_button_hover_color=self.COLOR_ENTRY_BORDER)
        fm.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        ec = dict(height=30, corner_radius=6,
                  font=ctk.CTkFont(family="Segoe UI", size=12),
                  fg_color=self.COLOR_ENTRY_BG, border_color=self.COLOR_ENTRY_BORDER,
                  text_color=self.COLOR_TEXT, placeholder_text_color=self.COLOR_TEXT_SEC)
        lc = dict(font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                  text_color=self.COLOR_TEXT_SEC, anchor="w")

        self.entries: dict[str, ctk.CTkEntry] = {}

        ctk.CTkLabel(fm, text="DATOS DEL PACIENTE",
                     font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                     text_color=self.COLOR_ACCENT, anchor="w",
                     ).pack(fill="x", padx=4, pady=(2, 4))

        # Cedula con selector
        ctk.CTkLabel(fm, text="Cedula", **lc).pack(fill="x", padx=4, pady=(2, 1))
        ced_fr = ctk.CTkFrame(fm, fg_color="transparent")
        ced_fr.pack(fill="x", padx=4, pady=(0, 2))

        self.opt_ced = ctk.CTkOptionMenu(
            ced_fr, values=["V-", "E-", "S/C"], width=60, height=30,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.COLOR_ENTRY_BG, button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            dropdown_fg_color=self.COLOR_PANEL, dropdown_hover_color=self.COLOR_ENTRY_BG,
            text_color=self.COLOR_TEXT, command=self._on_ced_tipo,
        )
        self.opt_ced.set("V-")
        self.opt_ced.pack(side="left", padx=(0, 4))

        self.e_ced = ctk.CTkEntry(ced_fr, placeholder_text="12345678", **ec)
        self.e_ced.pack(side="left", fill="x", expand=True)

        campos = [
            ("Primer Nombre *", "nombre1", ""),
            ("Segundo Nombre", "nombre2", "(Opcional)"),
            ("Primer Apellido *", "apellido1", ""),
            ("Segundo Apellido", "apellido2", "(Opcional)"),
            ("Fecha de Nacimiento *", "fecha_nacimiento", "DD/MM/AAAA"),
            ("Lugar de Nacimiento *", "lugar_nacimiento", ""),
        ]
        for lbl, key, ph in campos:
            ctk.CTkLabel(fm, text=lbl, **lc).pack(fill="x", padx=4, pady=(3, 1))
            e = ctk.CTkEntry(fm, placeholder_text=ph, **ec)
            e.pack(fill="x", padx=4, pady=(0, 1))
            self.entries[key] = e

        ctk.CTkLabel(fm, text="Estado Vital", **lc).pack(fill="x", padx=4, pady=(3, 1))
        self.opt_estado = ctk.CTkOptionMenu(
            fm, values=["Vivo", "Fallecido"], height=30,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.COLOR_ENTRY_BG, button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER, text_color=self.COLOR_TEXT,
            dropdown_fg_color=self.COLOR_PANEL, dropdown_hover_color=self.COLOR_ENTRY_BG,
        )
        self.opt_estado.set("Vivo")
        self.opt_estado.pack(fill="x", padx=4, pady=(0, 1))

        ctk.CTkFrame(fm, fg_color=self.COLOR_ENTRY_BORDER, height=1
                     ).pack(fill="x", padx=4, pady=6)

        ctk.CTkLabel(fm, text="TARJETA INDICE",
                     font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                     text_color=self.COLOR_ACCENT, anchor="w",
                     ).pack(fill="x", padx=4, pady=(0, 4))

        ctk.CTkLabel(fm, text="N. Historia * (XX-XX-XX)", **lc
                     ).pack(fill="x", padx=4, pady=(0, 1))
        self.entry_nh = ctk.CTkEntry(fm, placeholder_text="Ej: 03-77-34", **ec)
        self.entry_nh.pack(fill="x", padx=4, pady=(0, 3))
        self.entry_nh.bind("<KeyRelease>", lambda _: self._preview())

        self.pv = ctk.CTkFrame(fm, fg_color=self.COLOR_ENTRY_BG,
                               corner_radius=6, height=32)
        self.pv.pack(fill="x", padx=4, pady=(0, 3))
        self.pv.pack_propagate(False)

        pvi = ctk.CTkFrame(self.pv, fg_color="transparent")
        pvi.pack(fill="x", padx=8, pady=4)

        self.cbox = ctk.CTkFrame(pvi, fg_color="#444", width=18, height=18,
                                 corner_radius=4)
        self.cbox.pack(side="left", padx=(0, 6))
        self.cbox.pack_propagate(False)

        self.lbl_clr = ctk.CTkLabel(pvi, text="Ingrese N. Historia",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_TEXT_SEC)
        self.lbl_clr.pack(side="left")

        self.lbl_err = ctk.CTkLabel(fm, text="", wraplength=260, anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.COLOR_ERROR)
        self.lbl_err.pack(fill="x", padx=4, pady=(2, 2))

    # ==========================================================================
    #  MOSTRAR / OCULTAR FORM
    # ==========================================================================

    def _mostrar_form(self, titulo="Nuevo Ingreso"):
        if self._form_visible:
            self.lbl_ftitle.configure(text=titulo)
            return
        self._form_visible = True
        self.lbl_ftitle.configure(text=titulo)
        self.cuerpo.grid_columnconfigure(0, weight=55)
        self.cuerpo.grid_columnconfigure(1, weight=45)
        self.p_form.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def _cerrar_form(self):
        if not self._form_visible:
            return
        self._form_visible = False
        self.id_pac_sel = None
        self.id_tarj_sel = None
        self._limpiar()
        self.p_form.grid_forget()
        self.cuerpo.grid_columnconfigure(0, weight=1)
        self.cuerpo.grid_columnconfigure(1, weight=0)

    # ==========================================================================
    #  CEDULA
    # ==========================================================================

    def _on_ced_tipo(self, val):
        if val == "S/C":
            self.e_ced.delete(0, "end")
            self.e_ced.configure(state="disabled", placeholder_text="Sin cedula")
        else:
            self.e_ced.configure(state="normal", placeholder_text="12345678")

    def _get_cedula(self) -> str:
        t = self.opt_ced.get()
        if t == "S/C":
            return "S/C"
        n = self.e_ced.get().strip()
        return f"{t}{n}" if n else ""

    def _set_cedula(self, ced: str):
        if not ced or ced == "S/C":
            self.opt_ced.set("S/C")
            self.e_ced.configure(state="disabled", placeholder_text="Sin cedula")
            self.e_ced.delete(0, "end")
        elif ced.upper().startswith("E-"):
            self.opt_ced.set("E-")
            self.e_ced.configure(state="normal", placeholder_text="12345678")
            self._se(self.e_ced, ced[2:])
        else:
            self.opt_ced.set("V-")
            self.e_ced.configure(state="normal", placeholder_text="12345678")
            p = 2 if ced.upper().startswith("V-") else 0
            self._se(self.e_ced, ced[p:])

    # ==========================================================================
    #  BUSQUEDA
    # ==========================================================================

    def _on_crit(self, v):
        if v == "Todos":
            self.entry_busq.delete(0, "end")
            self._buscar_todo()

    def _buscar_todo(self):
        try:
            self._render(self.busq_ctrl.obtener_todos())
        except Exception as e:
            self._msg(f"Error: {e}", True)

    def _buscar(self):
        ct = self._crit_var.get()
        k = next((k for k, l in self.CRITERIOS if l == ct), "todos")
        v = self.entry_busq.get().strip()
        ok, res = self.busq_ctrl.buscar(k, v)
        if ok:
            self._render(res)
            self.lbl_msg.configure(text="")
        else:
            self._msg(str(res), True)

    def _render(self, regs):
        for w in self._filas:
            w.destroy()
        self._filas.clear()

        n = len(regs)
        self.lbl_cnt.configure(text=f"{n} resultado{'s' if n != 1 else ''}")

        if not regs:
            self._render_vacio()
            return

        for idx, r in enumerate(regs):
            bg = self.COLOR_ROW_ALT if idx % 2 == 0 else "transparent"
            f = ctk.CTkFrame(self.tscroll, fg_color=bg, corner_radius=3, height=28)
            f.grid(row=idx + 1, column=0, columnspan=len(self.COL_NAMES),
                   sticky="ew", pady=1)
            f.grid_propagate(False)

            for i, w in enumerate(self.COL_WIDTHS):
                f.grid_columnconfigure(i, weight=1, minsize=w)

            nm = r.nombre1
            if r.nombre2:
                nm += f" {r.nombre2}"
            nm += f" {r.apellido1}"
            if r.apellido2:
                nm += f" {r.apellido2}"

            hx = self._hex(r.num_historia)
            vals = [r.cedula, nm, r.fecha_nacimiento,
                    r.lugar_nacimiento, r.num_historia, None]

            for i, v in enumerate(vals):
                if i == 5:  # Color
                    cf = ctk.CTkFrame(f, fg_color="transparent")
                    cf.grid(row=0, column=i, sticky="ew", padx=4, pady=2)
                    ind = ctk.CTkFrame(cf, fg_color=hx, width=12, height=12,
                                       corner_radius=3)
                    ind.pack(side="left", padx=(0, 3))
                    ind.pack_propagate(False)
                    lb = ctk.CTkLabel(cf, text=r.color or "",
                        font=ctk.CTkFont(family="Segoe UI", size=10),
                        text_color=self.COLOR_TEXT, anchor="w")
                    lb.pack(side="left")
                    cf.bind("<Button-1>", lambda _, x=r: self._sel(x))
                    lb.bind("<Button-1>", lambda _, x=r: self._sel(x))
                else:
                    lb = ctk.CTkLabel(f, text=str(v or ""),
                        font=ctk.CTkFont(family="Segoe UI", size=10),
                        text_color=self.COLOR_TEXT, anchor="w")
                    lb.grid(row=0, column=i, sticky="ew", padx=6, pady=3)
                    lb.bind("<Button-1>", lambda _, x=r: self._sel(x))

            f.bind("<Button-1>", lambda _, x=r: self._sel(x))
            self._filas.append(f)

    def _render_vacio(self):
        fr = ctk.CTkFrame(self.tscroll, fg_color="transparent")
        fr.grid(row=1, column=0, columnspan=len(self.COL_NAMES), pady=30, sticky="ew")
        ctk.CTkLabel(fr, text="No se encontraron pacientes",
                     font=ctk.CTkFont(family="Segoe UI", size=13),
                     text_color=self.COLOR_TEXT_SEC).pack(pady=(0, 8))
        ctk.CTkButton(fr, text="Registrar Nuevo Paciente", width=180, height=30,
                      corner_radius=8,
                      font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                      fg_color=self.COLOR_SUCCESS, hover_color="#00B377",
                      text_color="#FFF", command=self._nuevo).pack()
        self._filas.append(fr)

    # ==========================================================================
    #  ACCIONES
    # ==========================================================================

    def _nuevo(self):
        self.id_pac_sel = None
        self.id_tarj_sel = None
        self._limpiar()
        self._mostrar_form("Nuevo Ingreso")
        self.entries["nombre1"].focus_set()

    def _sel(self, reg):
        """Selecciona usando id_paciente (funciona para multiples S/C)."""
        pac = self.pac_ctrl.obtener_paciente_por_id(reg.id_paciente)
        if not pac:
            self._msg("No se pudo cargar el paciente.", True)
            return

        self.id_pac_sel = pac.id
        tarj = self.tarj_ctrl.obtener_tarjeta_paciente(pac.id)
        self.id_tarj_sel = tarj.id if tarj else None

        self._set_cedula(pac.cedula)
        self._se(self.entries["nombre1"], pac.nombre1)
        self._se(self.entries["nombre2"], pac.nombre2 or "")
        self._se(self.entries["apellido1"], pac.apellido1)
        self._se(self.entries["apellido2"], pac.apellido2 or "")
        self._se(self.entries["fecha_nacimiento"], pac.fecha_nacimiento)
        self._se(self.entries["lugar_nacimiento"], pac.lugar_nacimiento)
        self.opt_estado.set("Vivo" if pac.estado_vital == 1 else "Fallecido")

        if tarj:
            self._se(self.entry_nh, tarj.num_historia)
        else:
            self.entry_nh.delete(0, "end")

        self._preview()
        self._mostrar_form("Editar Paciente")

    def _guardar(self):
        datos = self._recoger()
        if datos is None:
            return

        dp, nh = datos
        try:
            if self.id_pac_sel is not None:
                ok, msg = self.pac_ctrl.actualizar_paciente(self.id_pac_sel, dp)
                if not ok:
                    self._msg(msg, True)
                    return
                if self.id_tarj_sel is not None:
                    ok2, m2 = self.tarj_ctrl.actualizar_tarjeta(self.id_tarj_sel, nh)
                else:
                    ok2, m2 = self.tarj_ctrl.crear_tarjeta(self.id_pac_sel, nh)
                if not ok2:
                    self._msg(f"Paciente OK. Tarjeta: {m2}", True)
                else:
                    self._msg("Paciente y tarjeta actualizados.", False)
            else:
                ok, msg = self.pac_ctrl.registrar_paciente_con_tarjeta(dp, nh)
                self._msg(msg, not ok)

            if ok:
                self._limpiar()
                self.id_pac_sel = None
                self.id_tarj_sel = None
                self._buscar_todo()
        except Exception as e:
            self._msg(f"Error: {e}", True)

    def _eliminar(self):
        if self.id_pac_sel is None:
            self._msg("Seleccione un paciente de la lista primero.", True)
            return
        try:
            if self.id_tarj_sel:
                self.tarj_ctrl.eliminar_tarjeta(self.id_tarj_sel)
            ok, msg = self.pac_ctrl.eliminar_paciente(self.id_pac_sel)
            self._msg(msg, not ok)
            if ok:
                self._cerrar_form()
                self._buscar_todo()
        except Exception as e:
            self._msg(f"Error: {e}", True)

    # ==========================================================================
    #  PREVIEW COLOR
    # ==========================================================================

    def _preview(self):
        nh = self.entry_nh.get().strip()
        if not nh or not validar_formato_num_historia(nh):
            self.cbox.configure(fg_color="#444")
            t = "Formato requerido: XX-XX-XX" if nh else "Ingrese N. Historia"
            self.lbl_clr.configure(text=t, text_color=self.COLOR_TEXT_SEC)
            return
        try:
            i = obtener_color_por_num_historia(nh)
            self.cbox.configure(fg_color=i["hex"])
            self.lbl_clr.configure(text=i["nombre"], text_color=self.COLOR_TEXT)
        except ValueError:
            self.cbox.configure(fg_color="#444")
            self.lbl_clr.configure(text="Formato invalido", text_color=self.COLOR_ERROR)

    # ==========================================================================
    #  VALIDACION
    # ==========================================================================

    def _recoger(self):
        errs = []

        ced = self._get_cedula()
        if not ced:
            errs.append("• Cedula: ingrese el numero o seleccione S/C.")

        n1 = self.entries["nombre1"].get().strip()
        if not n1:
            errs.append("• Primer Nombre: campo obligatorio.")

        a1 = self.entries["apellido1"].get().strip()
        if not a1:
            errs.append("• Primer Apellido: campo obligatorio.")

        fecha = self.entries["fecha_nacimiento"].get().strip()
        if not fecha:
            errs.append("• Fecha Nac.: campo obligatorio (DD/MM/AAAA).")
        elif not self._fecha_ok(fecha):
            errs.append("• Fecha Nac.: formato invalido. Ejemplo: 21/02/2000.")

        lugar = self.entries["lugar_nacimiento"].get().strip()
        if not lugar:
            errs.append("• Lugar Nac.: campo obligatorio.")

        nh = self.entry_nh.get().strip()
        if not nh:
            errs.append("• N. Historia: campo obligatorio (XX-XX-XX).")
        elif not validar_formato_num_historia(nh):
            errs.append("• N. Historia: use 3 pares de digitos (ej: 03-77-34).")

        if errs:
            self.lbl_err.configure(text="\n".join(errs))
            return None

        self.lbl_err.configure(text="")

        return {
            "cedula": ced,
            "nombre1": n1,
            "nombre2": self.entries["nombre2"].get().strip() or None,
            "apellido1": a1,
            "apellido2": self.entries["apellido2"].get().strip() or None,
            "fecha_nacimiento": fecha.replace("-", "/"),
            "lugar_nacimiento": lugar,
            "estado_vital": 1 if self.opt_estado.get() == "Vivo" else 0,
        }, nh

    @staticmethod
    def _fecha_ok(v: str) -> bool:
        import re
        if not re.match(r"^\d{2}[/\-]\d{2}[/\-]\d{4}$", v):
            return False
        v = v.replace("-", "/")
        p = v.split("/")
        d, m, a = int(p[0]), int(p[1]), int(p[2])
        return 1 <= d <= 31 and 1 <= m <= 12 and 1900 <= a <= 2100

    # ==========================================================================
    #  UTILIDADES
    # ==========================================================================

    @staticmethod
    def _se(entry, val):
        entry.delete(0, "end")
        entry.insert(0, str(val))

    def _limpiar(self):
        for e in self.entries.values():
            e.configure(state="normal")
            e.delete(0, "end")
        self.e_ced.configure(state="normal")
        self.e_ced.delete(0, "end")
        self.entry_nh.delete(0, "end")
        self.opt_estado.set("Vivo")
        self.opt_ced.set("V-")
        self.e_ced.configure(placeholder_text="12345678")
        self.cbox.configure(fg_color="#444")
        self.lbl_clr.configure(text="Ingrese N. Historia", text_color=self.COLOR_TEXT_SEC)
        self.lbl_err.configure(text="")

    def _msg(self, t: str, err: bool = False):
        c = self.COLOR_ERROR if err else self.COLOR_SUCCESS
        if not t: c = self.COLOR_TEXT_SEC
        self.lbl_msg.configure(text=t, text_color=c)

    @staticmethod
    def _hex(nh: str) -> str:
        try:
            d = int(nh.split("-")[2][0])
            _, h = MAPA_COLORES[d]
            return h
        except (IndexError, ValueError, KeyError):
            return "#666"
