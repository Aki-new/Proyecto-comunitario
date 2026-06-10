"""
Vista del Tarjetero de Ingresos — SGI Salud.

Módulo para gestionar tarjetas de pacientes ingresados en servicios
hospitalarios. Permite visualizar por servicio qué pacientes ocupan
camas, registrar ingresos y dar de alta (egresos).

Componentes principales:
    - Panel lateral con lista de servicios y barras de ocupación.
    - Área central con vista de galería (tarjetas) o lista (tabla).
    - Popups modales para registrar ingreso, confirmar egreso y
      editar capacidad de camas.
    - Toggle conmutable entre modo Galería y modo Lista.

Relación con otros módulos:
    - Usa IngresoController para toda la lógica de negocio.
    - Usa CampoFecha (calendario_widget) para selección de fechas.
    - Usa ejecutar_en_hilo para operaciones de BD asíncronas.
"""

import datetime
import customtkinter as ctk
from controllers.ingreso_controller import IngresoController
from utils.date_utils import parse_date
from views.calendario_widget import CampoFecha
from utils.hilo_trabajo import ejecutar_en_hilo


class TarjeteroView(ctk.CTkFrame):
    """Módulo principal del Tarjetero de Ingresos.

    Muestra los servicios hospitalarios y los pacientes ingresados en cada
    uno, con opciones para registrar ingresos y egresos.

    Atributos:
        controlador:             Instancia de IngresoController.
        servicio_seleccionado:   ID del servicio actualmente seleccionado.
        modo_vista:              'galeria' o 'lista' — modo de visualización.
        _botones_servicios:      Mapa id_servicio → CTkFrame del panel lateral.
        _resumen_servicios:      Lista de resúmenes de servicios (cache).
        _resumen_actual:         Resumen del servicio seleccionado (cache).
    """

    def __init__(self, parent, tema=None, fuentes=None, **kwargs):
        """Inicializa la vista del tarjetero.

        Args:
            parent:  Widget padre donde se coloca este frame.
            tema:    Dict de colores del tema activo.
            fuentes: Dict de tamaños de fuente activos.
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        # ── Tema y fuentes ──
        t = tema or {}
        self.C_FONDO = t.get("fondo", "#0F1923")
        self.C_PANEL = t.get("panel", "#182633")
        self.C_ACENTO = t.get("acento", "#00A8E8")
        self.C_ACENTO_HOVER = t.get("acento_hover", "#007BB5")
        self.C_TEXTO = t.get("texto", "#E8EDF2")
        self.C_TEXTO_SEC = t.get("texto_secundario", "#8899AA")
        self.C_ENTRADA = t.get("entrada_fondo", "#1E3044")
        self.C_BORDE = t.get("entrada_borde", "#2A4158")
        self.C_ERROR = t.get("error", "#FF4C6A")
        self.C_EXITO = t.get("exito", "#00D68F")
        self.C_PELIGRO = t.get("peligro", "#FF4C6A")
        self.C_PELIGRO_HOVER = t.get("peligro_hover", "#D93A5A")
        self.C_FILA_ALT = t.get("fila_alterna", "#1A2D3D")
        self.C_BOTON_HOVER = t.get("boton_hover", "#1A2D3D")
        self.C_SEPARADOR = t.get("separador", "#2A4158")
        self._tema_dict = t

        f = fuentes or {}
        self.F_BASE = f.get("base", 12)
        self.F_TITULO = f.get("titulo", 18)
        self.F_SUBTITULO = f.get("subtitulo", 14)
        self.F_ETIQUETA = f.get("etiqueta", 10)
        self._fuentes_dict = f

        # ── Estado ──
        self.controlador = IngresoController()
        self.servicio_seleccionado = None
        self.modo_vista = "galeria"
        self._botones_servicios: dict[int, ctk.CTkFrame] = {}
        self._resumen_servicios: list[dict] = []
        self._resumen_actual: dict | None = None
        self._widgets_contenido: list = []

        # ── Construir interfaz ──
        self._construir_interfaz()
        self._cargar_servicios()

    # ══════════════════════════════════════════════════════════════════
    #  CONSTRUCCIÓN DE INTERFAZ
    # ══════════════════════════════════════════════════════════════════

    def _construir_interfaz(self):
        """Crea la estructura principal: barra superior, panel lateral y contenido."""
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self._construir_barra_superior()
        self._construir_panel_servicios()
        self._construir_area_contenido()
        self._construir_barra_mensajes()

    def _construir_barra_superior(self):
        """Barra superior con título y toggle de vista."""
        barra = ctk.CTkFrame(self, fg_color=self.C_PANEL, corner_radius=8, height=50)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 6))
        barra.grid_propagate(False)
        barra.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            barra, text="🏥 Tarjetero de Ingresos",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_TITULO, weight="bold"),
            text_color=self.C_TEXTO,
        ).grid(row=0, column=0, padx=14, pady=10, sticky="w")

        self.toggle_vista = ctk.CTkSegmentedButton(
            barra, values=["🔲 Galería", "≡ Lista"],
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.C_ENTRADA, selected_color=self.C_ACENTO,
            selected_hover_color=self.C_ACENTO_HOVER,
            unselected_color=self.C_ENTRADA,
            unselected_hover_color=self.C_BORDE,
            text_color=self.C_TEXTO,
            command=self._al_cambiar_modo_vista,
        )
        self.toggle_vista.set("🔲 Galería")
        self.toggle_vista.grid(row=0, column=2, padx=14, pady=10, sticky="e")

    def _construir_panel_servicios(self):
        """Panel lateral con lista scrollable de servicios hospitalarios."""
        self.panel_lateral = ctk.CTkFrame(
            self, fg_color=self.C_PANEL, corner_radius=8, width=210,
        )
        self.panel_lateral.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=0)
        self.panel_lateral.grid_propagate(False)
        self.panel_lateral.grid_rowconfigure(1, weight=1)
        self.panel_lateral.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.panel_lateral, text="SERVICIOS",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
            text_color=self.C_TEXTO_SEC, anchor="w",
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")

        self.scroll_servicios = ctk.CTkScrollableFrame(
            self.panel_lateral, fg_color="transparent",
            scrollbar_button_color=self.C_ENTRADA,
            scrollbar_button_hover_color=self.C_ACENTO,
        )
        self.scroll_servicios.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self.scroll_servicios.grid_columnconfigure(0, weight=1)

    def _construir_area_contenido(self):
        """Área principal donde se muestra el contenido del servicio seleccionado."""
        self.area_contenido = ctk.CTkFrame(
            self, fg_color=self.C_PANEL, corner_radius=8,
        )
        self.area_contenido.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=0)
        self.area_contenido.grid_columnconfigure(0, weight=1)
        self.area_contenido.grid_rowconfigure(1, weight=1)

        # Cabecera del servicio
        self.cabecera_servicio = ctk.CTkFrame(
            self.area_contenido, fg_color="transparent", height=50,
        )
        self.cabecera_servicio.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        self.cabecera_servicio.grid_columnconfigure(0, weight=1)

        self.etiqueta_nombre_servicio = ctk.CTkLabel(
            self.cabecera_servicio, text="Seleccione un servicio",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_SUBTITULO, weight="bold"),
            text_color=self.C_TEXTO, anchor="w",
        )
        self.etiqueta_nombre_servicio.grid(row=0, column=0, sticky="w")

        self.etiqueta_conteo_camas = ctk.CTkLabel(
            self.cabecera_servicio, text="",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_TEXTO_SEC, anchor="w",
        )
        self.etiqueta_conteo_camas.grid(row=1, column=0, sticky="w")

        marco_botones = ctk.CTkFrame(self.cabecera_servicio, fg_color="transparent")
        marco_botones.grid(row=0, column=1, rowspan=2, sticky="e", padx=(10, 0))

        self.boton_ingresar = ctk.CTkButton(
            marco_botones, text="+ Registrar Ingreso",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.C_ACENTO, hover_color=self.C_ACENTO_HOVER,
            text_color="#FFFFFF", corner_radius=6, height=30,
            command=self._abrir_popup_ingreso,
        )
        self.boton_ingresar.pack(side="left", padx=(0, 6))

        self.boton_editar_camas = ctk.CTkButton(
            marco_botones, text="⚙ Editar Camas",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.C_ENTRADA, hover_color=self.C_BORDE,
            text_color=self.C_TEXTO, corner_radius=6, height=30,
            command=self._abrir_popup_editar_camas,
        )
        self.boton_editar_camas.pack(side="left")

        # Separador
        ctk.CTkFrame(
            self.area_contenido, fg_color=self.C_SEPARADOR, height=1,
        ).grid(row=0, column=0, sticky="sew", padx=10)

        # Contenedor scrollable para el contenido
        self.contenido_scroll = ctk.CTkScrollableFrame(
            self.area_contenido, fg_color="transparent",
            scrollbar_button_color=self.C_ENTRADA,
            scrollbar_button_hover_color=self.C_ACENTO,
        )
        self.contenido_scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

    def _construir_barra_mensajes(self):
        """Barra inferior para mensajes de feedback."""
        self.etiqueta_mensaje = ctk.CTkLabel(
            self, text="", height=24,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_TEXTO_SEC,
        )
        self.etiqueta_mensaje.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 2))

    # ══════════════════════════════════════════════════════════════════
    #  CARGA DE DATOS
    # ══════════════════════════════════════════════════════════════════

    def _cargar_servicios(self):
        """Carga la lista de servicios y sus resúmenes en hilo secundario."""
        ejecutar_en_hilo(
            self,
            tarea=self.controlador.obtener_resumen_general,
            callback_exito=self._on_servicios_cargados,
            callback_error=lambda e: self._mostrar_mensaje(f"Error al cargar servicios: {e}", True),
        )

    def _on_servicios_cargados(self, resumenes):
        """Callback: renderiza el panel lateral con los servicios recibidos."""
        self._resumen_servicios = resumenes
        self._renderizar_panel_servicios()

        # Seleccionar el primer servicio automáticamente
        if resumenes:
            primer_id = resumenes[0]["servicio"].id
            self._seleccionar_servicio(primer_id)

    def _cargar_contenido_servicio(self, id_servicio):
        """Carga el detalle del servicio seleccionado en hilo secundario."""
        ejecutar_en_hilo(
            self,
            tarea=lambda: self.controlador.obtener_resumen_servicio(id_servicio),
            callback_exito=self._on_contenido_cargado,
            callback_error=lambda e: self._mostrar_mensaje(f"Error: {e}", True),
        )

    def _on_contenido_cargado(self, resumen):
        """Callback: renderiza el contenido del servicio seleccionado."""
        if resumen is None:
            return
        self._resumen_actual = resumen
        servicio = resumen["servicio"]
        ocupadas = resumen["ocupadas"]
        total = resumen["total_camas"]

        self.etiqueta_nombre_servicio.configure(text=servicio.nombre)
        self.etiqueta_conteo_camas.configure(
            text=f"{ocupadas}/{total} camas ocupadas — {resumen['disponibles']} disponibles"
        )

        if self.modo_vista == "galeria":
            self._renderizar_galeria(resumen["ingresos"])
        else:
            self._renderizar_lista(resumen["ingresos"])

    # ══════════════════════════════════════════════════════════════════
    #  PANEL LATERAL DE SERVICIOS
    # ══════════════════════════════════════════════════════════════════

    def _renderizar_panel_servicios(self):
        """Redibuja el panel lateral con los servicios y barras de ocupación."""
        for widget in self.scroll_servicios.winfo_children():
            widget.destroy()
        self._botones_servicios.clear()

        for indice, resumen in enumerate(self._resumen_servicios):
            servicio = resumen["servicio"]
            ocupadas = resumen["ocupadas"]
            total = resumen["total_camas"]
            porcentaje = ocupadas / total if total > 0 else 0

            # Color de la barra según ocupación
            if porcentaje < 0.5:
                color_barra = self.C_EXITO
            elif porcentaje < 0.8:
                color_barra = "#FFB800"
            else:
                color_barra = self.C_PELIGRO

            es_seleccionado = servicio.id == self.servicio_seleccionado
            color_fondo = self.C_ACENTO if es_seleccionado else "transparent"

            marco = ctk.CTkFrame(
                self.scroll_servicios, fg_color=color_fondo,
                corner_radius=8, cursor="hand2",
            )
            marco.grid(row=indice, column=0, sticky="ew", padx=4, pady=2)
            marco.grid_columnconfigure(0, weight=1)

            # Nombre del servicio
            etiqueta_nombre = ctk.CTkLabel(
                marco, text=servicio.nombre,
                font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
                text_color="#FFFFFF" if es_seleccionado else self.C_TEXTO,
                anchor="w",
            )
            etiqueta_nombre.grid(row=0, column=0, padx=10, pady=(8, 0), sticky="ew")

            # Indicador de ocupación
            etiqueta_ocupacion = ctk.CTkLabel(
                marco, text=f"{ocupadas}/{total} camas",
                font=ctk.CTkFont(family="Segoe UI", size=max(9, self.F_ETIQUETA - 2)),
                text_color="#FFFFFF" if es_seleccionado else self.C_TEXTO_SEC,
                anchor="w",
            )
            etiqueta_ocupacion.grid(row=1, column=0, padx=10, pady=0, sticky="ew")

            # Barra de progreso
            barra = ctk.CTkProgressBar(
                marco, height=6, corner_radius=3,
                fg_color=self.C_ENTRADA,
                progress_color=color_barra,
            )
            barra.set(porcentaje)
            barra.grid(row=2, column=0, padx=10, pady=(2, 8), sticky="ew")

            # Bind click en todo el marco y sus hijos
            id_serv = servicio.id
            for widget in [marco, etiqueta_nombre, etiqueta_ocupacion, barra]:
                widget.bind("<Button-1>", lambda _, sid=id_serv: self._seleccionar_servicio(sid))

            self._botones_servicios[servicio.id] = marco

    def _seleccionar_servicio(self, id_servicio):
        """Selecciona un servicio y carga su contenido."""
        self.servicio_seleccionado = id_servicio
        # Actualizar estilos del panel lateral
        for sid, marco in self._botones_servicios.items():
            if sid == id_servicio:
                marco.configure(fg_color=self.C_ACENTO)
                for child in marco.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text_color="#FFFFFF")
            else:
                marco.configure(fg_color="transparent")
                for child in marco.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        idx = list(marco.winfo_children()).index(child)
                        child.configure(
                            text_color=self.C_TEXTO if idx == 0 else self.C_TEXTO_SEC
                        )
        self._cargar_contenido_servicio(id_servicio)

    # ══════════════════════════════════════════════════════════════════
    #  MODO GALERÍA (tarjetas)
    # ══════════════════════════════════════════════════════════════════

    def _renderizar_galeria(self, ingresos):
        """Renderiza las tarjetas de pacientes ingresados en modo galería."""
        self._limpiar_contenido()

        if not ingresos:
            self._renderizar_estado_vacio()
            return

        self.contenido_scroll.bind("<Configure>", self._reconfigurar_grilla)

        for indice, ingreso in enumerate(ingresos):
            tarjeta = self._crear_tarjeta_paciente(ingreso)
            self._widgets_contenido.append(tarjeta)

        self._posicionar_tarjetas()

    def _crear_tarjeta_paciente(self, ingreso):
        """Crea una tarjeta visual para un paciente ingresado.

        Args:
            ingreso: IngresoDetalle con datos del paciente.

        Returns:
            CTkFrame con la tarjeta construida.
        """
        tarjeta = ctk.CTkFrame(
            self.contenido_scroll, fg_color=self.C_FONDO,
            corner_radius=10, border_width=1, border_color=self.C_BORDE,
            cursor="hand2",
        )

        # Contenedor interno con borde de color
        franja_color = ctk.CTkFrame(
            tarjeta, fg_color=ingreso.color_hex or "#888888",
            width=6, corner_radius=3,
        )
        franja_color.pack(side="left", fill="y", padx=(6, 0), pady=6)

        contenido = ctk.CTkFrame(tarjeta, fg_color="transparent")
        contenido.pack(side="left", fill="both", expand=True, padx=(8, 10), pady=8)

        # Nombre del paciente
        ctk.CTkLabel(
            contenido, text=ingreso.nombre_completo,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA + 1, weight="bold"),
            text_color=self.C_TEXTO, anchor="w", wraplength=180,
        ).pack(fill="x")

        # Cédula
        ctk.CTkLabel(
            contenido, text=ingreso.cedula,
            font=ctk.CTkFont(family="Segoe UI", size=max(9, self.F_ETIQUETA - 1)),
            text_color=self.C_TEXTO_SEC, anchor="w",
        ).pack(fill="x")

        # Número de historia
        ctk.CTkLabel(
            contenido, text=f"N° {ingreso.num_historia}",
            font=ctk.CTkFont(family="Segoe UI", size=max(9, self.F_ETIQUETA - 1)),
            text_color=self.C_TEXTO_SEC, anchor="w",
        ).pack(fill="x")

        # Días de ingreso
        dias = self._calcular_dias_ingreso(ingreso.fecha_ingreso)
        texto_dias = f"{dias} día{'s' if dias != 1 else ''}"
        ctk.CTkLabel(
            contenido, text=texto_dias,
            font=ctk.CTkFont(family="Segoe UI", size=max(9, self.F_ETIQUETA - 1)),
            text_color=self.C_ACENTO, anchor="w",
        ).pack(fill="x", pady=(2, 0))

        # Bind click en toda la tarjeta
        id_ingreso = ingreso.id
        for widget in [tarjeta, franja_color, contenido] + list(contenido.winfo_children()):
            widget.bind("<Button-1>", lambda _, iid=id_ingreso, ing=ingreso: self._abrir_popup_egreso(ing))

        return tarjeta

    def _posicionar_tarjetas(self):
        """Posiciona las tarjetas en una grilla responsiva."""
        ancho = self.contenido_scroll.winfo_width()
        columnas = max(1, ancho // 220)

        for i in range(columnas):
            self.contenido_scroll.grid_columnconfigure(i, weight=1)

        for indice, tarjeta in enumerate(self._widgets_contenido):
            fila = indice // columnas
            col = indice % columnas
            tarjeta.grid(row=fila, column=col, padx=4, pady=4, sticky="nsew")

    def _reconfigurar_grilla(self, event=None):
        """Recalcula columnas cuando cambia el ancho del contenedor."""
        if self.modo_vista != "galeria" or not self._widgets_contenido:
            return
        self._posicionar_tarjetas()

    # ══════════════════════════════════════════════════════════════════
    #  MODO LISTA (tabla)
    # ══════════════════════════════════════════════════════════════════

    def _renderizar_lista(self, ingresos):
        """Renderiza los pacientes ingresados en formato tabla."""
        self._limpiar_contenido()

        if not ingresos:
            self._renderizar_estado_vacio()
            return

        # Desligar configuración de grilla de galería
        self.contenido_scroll.unbind("<Configure>")

        # Cabecera de la tabla
        encabezados = ["Paciente", "Cédula", "N° Historia", "Color", "Ingreso", "Días", "Acción"]
        pesos = [3, 2, 1, 1, 1, 1, 1]

        cabecera = ctk.CTkFrame(self.contenido_scroll, fg_color=self.C_ENTRADA, height=32, corner_radius=6)
        cabecera.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 4))
        cabecera.grid_propagate(False)
        for i, (texto, peso) in enumerate(zip(encabezados, pesos)):
            cabecera.grid_columnconfigure(i, weight=peso, uniform="columna_lista_ingresos")
            ctk.CTkLabel(
                cabecera, text=texto,
                font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
                text_color=self.C_TEXTO, anchor="w",
                width=10,
            ).grid(row=0, column=i, padx=8, pady=6, sticky="ew")

        self.contenido_scroll.grid_columnconfigure(0, weight=1)

        # Filas de datos
        for indice, ingreso in enumerate(ingresos):
            color_fila = self.C_FILA_ALT if indice % 2 == 0 else "transparent"
            fila = ctk.CTkFrame(
                self.contenido_scroll, fg_color=color_fila, height=36, corner_radius=0,
            )
            fila.grid(row=indice + 1, column=0, sticky="ew", padx=2)
            fila.grid_propagate(False)
            for j, peso in enumerate(pesos):
                fila.grid_columnconfigure(j, weight=peso, uniform="columna_lista_ingresos")

            dias = self._calcular_dias_ingreso(ingreso.fecha_ingreso)
            valores = [
                ingreso.nombre_completo,
                ingreso.cedula,
                ingreso.num_historia,
                None,  # Color (se maneja aparte)
                ingreso.fecha_ingreso,
                str(dias),
                None,  # Acción
            ]

            for j, valor in enumerate(valores):
                if j == 3:
                    # Columna de color: cuadrado + nombre
                    marco_color = ctk.CTkFrame(fila, fg_color="transparent")
                    marco_color.grid(row=0, column=j, padx=8, pady=4, sticky="ew")
                    cuadro = ctk.CTkFrame(
                        marco_color, fg_color=ingreso.color_hex or "#888888",
                        width=14, height=14, corner_radius=3,
                    )
                    cuadro.pack(side="left", padx=(0, 4))
                    cuadro.pack_propagate(False)
                    ctk.CTkLabel(
                        marco_color, text=ingreso.color_nombre or "",
                        font=ctk.CTkFont(family="Segoe UI", size=max(9, self.F_ETIQUETA - 1)),
                        text_color=self.C_TEXTO_SEC,
                    ).pack(side="left")
                elif j == 6:
                    # Columna de acción: botón de egreso
                    boton_alta = ctk.CTkButton(
                        fila, text="Dar de Alta", width=80, height=24,
                        font=ctk.CTkFont(family="Segoe UI", size=max(9, self.F_ETIQUETA - 1)),
                        fg_color=self.C_PELIGRO, hover_color=self.C_PELIGRO_HOVER,
                        text_color="#FFFFFF", corner_radius=4,
                        command=lambda ing=ingreso: self._abrir_popup_egreso(ing),
                    )
                    boton_alta.grid(row=0, column=j, padx=8, pady=4, sticky="w")
                else:
                    ctk.CTkLabel(
                        fila, text=valor or "",
                        font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
                        text_color=self.C_TEXTO, anchor="w",
                        width=10,
                    ).grid(row=0, column=j, padx=8, pady=6, sticky="ew")

            self._widgets_contenido.append(fila)

    # ══════════════════════════════════════════════════════════════════
    #  ESTADO VACÍO
    # ══════════════════════════════════════════════════════════════════

    def _renderizar_estado_vacio(self):
        """Muestra un mensaje cuando no hay pacientes ingresados."""
        marco = ctk.CTkFrame(self.contenido_scroll, fg_color="transparent")
        marco.pack(expand=True, fill="both", pady=60)

        ctk.CTkLabel(
            marco, text="🛏️",
            font=ctk.CTkFont(size=48),
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            marco, text="Sin pacientes ingresados",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_SUBTITULO, weight="bold"),
            text_color=self.C_TEXTO_SEC,
        ).pack()

        if self._resumen_actual:
            disp = self._resumen_actual.get("disponibles", 0)
            ctk.CTkLabel(
                marco, text=f"{disp} camas disponibles",
                font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
                text_color=self.C_TEXTO_SEC,
            ).pack(pady=(4, 0))

        self._widgets_contenido.append(marco)

    # ══════════════════════════════════════════════════════════════════
    #  POPUP: REGISTRAR INGRESO
    # ══════════════════════════════════════════════════════════════════

    def _abrir_popup_ingreso(self):
        """Abre un popup modal para registrar un nuevo ingreso.

        El popup reutiliza el patrón de filtros de PacientesView (cédula,
        nombre, apellido, N° historia) para buscar pacientes disponibles
        (con tarjeta y no ingresados). Sin campo de observaciones.
        """
        if self.servicio_seleccionado is None:
            self._mostrar_mensaje("Seleccione un servicio primero.", True)
            return

        resumen = self._resumen_actual
        if resumen and resumen["disponibles"] <= 0:
            self._mostrar_mensaje("No hay camas disponibles en este servicio.", True)
            return

        nombre_servicio = resumen["servicio"].nombre if resumen else "Servicio"
        disponibles = resumen["disponibles"] if resumen else 0

        popup = ctk.CTkToplevel(self)
        popup.title(f"Registrar Ingreso — {nombre_servicio}")
        popup.geometry("620x560")
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.configure(fg_color=self.C_FONDO)

        # Centrar popup
        popup.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 620) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 560) // 2
        popup.geometry(f"+{x}+{y}")

        # ── Cabecera ──
        cabecera = ctk.CTkFrame(popup, fg_color=self.C_PANEL, corner_radius=8)
        cabecera.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            cabecera, text=f"Registrar Ingreso — {nombre_servicio}",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_SUBTITULO, weight="bold"),
            text_color=self.C_TEXTO, anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            cabecera, text=f"{disponibles} cama{'s' if disponibles != 1 else ''} disponible{'s' if disponibles != 1 else ''}",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_EXITO, anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 8))

        # ── Barra de filtros (reutiliza patrón de PacientesView) ──
        marco_filtros = ctk.CTkFrame(popup, fg_color="transparent")
        marco_filtros.pack(fill="x", padx=16, pady=(0, 4))
        marco_filtros.grid_columnconfigure(1, weight=1)

        # Selector de criterio
        CRITERIOS = [
            ("todos",        "Todos"),
            ("cedula",       "Cédula"),
            ("nombre",       "Nombre"),
            ("apellido",     "Apellido"),
            ("num_historia", "N° Historia"),
        ]
        criterio_var = ctk.StringVar(value="todos")

        ctk.CTkLabel(
            marco_filtros, text="Filtrar por:",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_TEXTO_SEC,
        ).grid(row=0, column=0, padx=(0, 6), sticky="w")

        selector_criterio = ctk.CTkOptionMenu(
            marco_filtros, values=[c[1] for c in CRITERIOS],
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.C_ENTRADA, button_color=self.C_BORDE,
            button_hover_color=self.C_ACENTO, text_color=self.C_TEXTO,
            dropdown_fg_color=self.C_PANEL, dropdown_text_color=self.C_TEXTO,
            dropdown_hover_color=self.C_ACENTO,
            width=120, height=30,
            command=lambda v: criterio_var.set(
                next(c[0] for c in CRITERIOS if c[1] == v)
            ),
        )
        selector_criterio.set("Todos")
        selector_criterio.grid(row=0, column=0, padx=(70, 6), sticky="w")

        entrada_busqueda = ctk.CTkEntry(
            marco_filtros, placeholder_text="Escriba para buscar pacientes disponibles...",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            fg_color=self.C_ENTRADA, border_color=self.C_BORDE,
            text_color=self.C_TEXTO, height=30,
        )
        entrada_busqueda.grid(row=0, column=1, padx=(0, 6), sticky="ew")

        boton_buscar = ctk.CTkButton(
            marco_filtros, text="🔍 Buscar", width=80, height=30,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.C_ACENTO, hover_color=self.C_ACENTO_HOVER,
            text_color="#FFFFFF", corner_radius=6,
        )
        boton_buscar.grid(row=0, column=2, sticky="e")

        # ── Tabla de resultados ──
        marco_tabla = ctk.CTkFrame(popup, fg_color=self.C_PANEL, corner_radius=8)
        marco_tabla.pack(fill="both", expand=True, padx=16, pady=(4, 6))
        marco_tabla.grid_columnconfigure(0, weight=1)
        marco_tabla.grid_rowconfigure(1, weight=1)

        # Cabecera de tabla
        encabezados = ["", "Paciente", "Cédula", "N° Historia"]
        pesos_col = [0, 3, 2, 1]

        cabecera_tabla = ctk.CTkFrame(marco_tabla, fg_color=self.C_ENTRADA, height=28, corner_radius=6)
        cabecera_tabla.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        cabecera_tabla.grid_propagate(False)
        for i, (txt, peso) in enumerate(zip(encabezados, pesos_col)):
            cabecera_tabla.grid_columnconfigure(i, weight=peso)
            if txt:
                ctk.CTkLabel(
                    cabecera_tabla, text=txt,
                    font=ctk.CTkFont(family="Segoe UI", size=max(9, self.F_ETIQUETA - 1), weight="bold"),
                    text_color=self.C_TEXTO, anchor="w",
                ).grid(row=0, column=i, padx=8, pady=4, sticky="w")

        scroll_resultados = ctk.CTkScrollableFrame(
            marco_tabla, fg_color="transparent",
            scrollbar_button_color=self.C_ENTRADA,
            scrollbar_button_hover_color=self.C_ACENTO,
        )
        scroll_resultados.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))
        scroll_resultados.grid_columnconfigure(0, weight=1)

        # ── Sección inferior: paciente seleccionado + fecha + botón ──
        marco_inferior = ctk.CTkFrame(popup, fg_color=self.C_PANEL, corner_radius=8)
        marco_inferior.pack(fill="x", padx=16, pady=(0, 6))
        marco_inferior.grid_columnconfigure(0, weight=1)

        # Paciente seleccionado
        etiqueta_seleccion = ctk.CTkLabel(
            marco_inferior, text="⬆ Seleccione un paciente de la tabla",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_TEXTO_SEC, anchor="w",
        )
        etiqueta_seleccion.grid(row=0, column=0, columnspan=3, padx=14, pady=(10, 4), sticky="ew")

        # Fecha de ingreso
        ctk.CTkLabel(
            marco_inferior, text="Fecha ingreso:",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_TEXTO_SEC, anchor="w",
        ).grid(row=1, column=0, padx=(14, 4), pady=(0, 10), sticky="w")

        campo_fecha = CampoFecha(marco_inferior, tema=self._tema_dict, fuente_tamano=self._fuentes_dict)
        campo_fecha.grid(row=1, column=1, padx=4, pady=(0, 10), sticky="w")
        hoy = datetime.datetime.now().strftime("%d-%m-%Y")
        campo_fecha.establecer_fecha(hoy)

        # Botón de ingreso prominente
        self._boton_confirmar_ingreso = ctk.CTkButton(
            marco_inferior, text="✓ Registrar Ingreso", width=160, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE, weight="bold"),
            fg_color=self.C_EXITO, hover_color="#00B377",
            text_color="#FFFFFF", corner_radius=8,
            state="disabled",
        )
        self._boton_confirmar_ingreso.grid(row=1, column=2, padx=(4, 14), pady=(0, 10), sticky="e")

        # ── Mensaje de error + botón cancelar ──
        marco_pie = ctk.CTkFrame(popup, fg_color="transparent")
        marco_pie.pack(fill="x", padx=16, pady=(0, 10))
        marco_pie.grid_columnconfigure(0, weight=1)

        etiqueta_error_popup = ctk.CTkLabel(
            marco_pie, text="", height=18,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_ERROR, anchor="w",
        )
        etiqueta_error_popup.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            marco_pie, text="Cancelar", width=90, height=28,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            fg_color=self.C_ENTRADA, hover_color=self.C_BORDE,
            text_color=self.C_TEXTO, corner_radius=6,
            command=popup.destroy,
        ).grid(row=0, column=1, sticky="e")

        # ═══════════════════════════════════════════════════════════
        #  Lógica interna del popup
        # ═══════════════════════════════════════════════════════════

        estado_popup = {"id_paciente": None}

        def _seleccionar_paciente_popup(paciente):
            estado_popup["id_paciente"] = paciente["id"]
            nombre = paciente.get("nombre_completo", "")
            cedula = paciente.get("cedula", "S/C")
            num_h = paciente.get("num_historia", "")
            color_h = paciente.get("color_hex", "#888")
            etiqueta_seleccion.configure(
                text=f"✓ {nombre} — {cedula} — N° {num_h}",
                text_color=self.C_EXITO,
            )
            self._boton_confirmar_ingreso.configure(state="normal")
            etiqueta_error_popup.configure(text="")
            # Resaltar fila seleccionada
            for w in scroll_resultados.winfo_children():
                w.configure(fg_color="transparent")
            # No se puede saber cuál es la fila directamente, pero la selección visual ya está en el label

        def _buscar_pacientes_popup(*args):
            termino = entrada_busqueda.get().strip()
            criterio = criterio_var.get()
            if len(termino) < 1 and criterio != "todos":
                for w in scroll_resultados.winfo_children():
                    w.destroy()
                return
            if criterio == "todos" and len(termino) < 2:
                for w in scroll_resultados.winfo_children():
                    w.destroy()
                return
            ejecutar_en_hilo(
                popup,
                tarea=lambda: self.controlador.buscar_pacientes_por_filtro(criterio, termino),
                callback_exito=_renderizar_resultados_popup,
                callback_error=lambda e: etiqueta_error_popup.configure(text=str(e)),
            )

        def _renderizar_resultados_popup(resultados):
            for w in scroll_resultados.winfo_children():
                w.destroy()
            if not resultados:
                ctk.CTkLabel(
                    scroll_resultados, text="No se encontraron pacientes disponibles.",
                    font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
                    text_color=self.C_TEXTO_SEC,
                ).pack(pady=20)
                return

            for i, pac in enumerate(resultados):
                color_fila = self.C_FILA_ALT if i % 2 == 0 else "transparent"
                fila = ctk.CTkFrame(scroll_resultados, fg_color=color_fila, cursor="hand2", height=32)
                fila.pack(fill="x", pady=1)
                fila.pack_propagate(False)
                fila.grid_columnconfigure(1, weight=3)
                fila.grid_columnconfigure(2, weight=2)
                fila.grid_columnconfigure(3, weight=1)

                # Cuadrado de color
                cuadro = ctk.CTkFrame(
                    fila, fg_color=pac.get("color_hex", "#888"),
                    width=14, height=14, corner_radius=3,
                )
                cuadro.grid(row=0, column=0, padx=(8, 4), pady=8)
                cuadro.grid_propagate(False)

                # Nombre
                lbl_nombre = ctk.CTkLabel(
                    fila, text=pac.get("nombre_completo", ""),
                    font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
                    text_color=self.C_TEXTO, anchor="w",
                )
                lbl_nombre.grid(row=0, column=1, padx=4, sticky="ew")

                # Cédula
                lbl_cedula = ctk.CTkLabel(
                    fila, text=pac.get("cedula", "S/C"),
                    font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
                    text_color=self.C_TEXTO_SEC, anchor="w",
                )
                lbl_cedula.grid(row=0, column=2, padx=4, sticky="ew")

                # N° Historia
                lbl_historia = ctk.CTkLabel(
                    fila, text=pac.get("num_historia", ""),
                    font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
                    text_color=self.C_TEXTO_SEC, anchor="w",
                )
                lbl_historia.grid(row=0, column=3, padx=(4, 8), sticky="ew")

                for w in [fila, cuadro, lbl_nombre, lbl_cedula, lbl_historia]:
                    w.bind("<Button-1>", lambda _, p=pac, f=fila: _on_click_fila(p, f))

        def _on_click_fila(paciente, fila_widget):
            """Selecciona paciente y resalta la fila clickeada."""
            # Resaltar fila
            for w in scroll_resultados.winfo_children():
                idx = list(scroll_resultados.winfo_children()).index(w)
                w.configure(fg_color=self.C_FILA_ALT if idx % 2 == 0 else "transparent")
            fila_widget.configure(fg_color=self.C_ACENTO)
            # Seleccionar paciente
            _seleccionar_paciente_popup(paciente)

        # Debounce para búsqueda
        _debounce_id = [None]

        def _on_keystroke(*args):
            if _debounce_id[0]:
                popup.after_cancel(_debounce_id[0])
            _debounce_id[0] = popup.after(300, _buscar_pacientes_popup)

        entrada_busqueda.bind("<KeyRelease>", _on_keystroke)
        boton_buscar.configure(command=_buscar_pacientes_popup)

        def _confirmar_ingreso():
            if estado_popup["id_paciente"] is None:
                etiqueta_error_popup.configure(text="Seleccione un paciente primero.")
                return
            fecha = campo_fecha.obtener_fecha().strip()
            if not fecha:
                etiqueta_error_popup.configure(text="La fecha de ingreso es obligatoria.")
                return

            datos = {
                "id_paciente": estado_popup["id_paciente"],
                "id_servicio": self.servicio_seleccionado,
                "fecha_ingreso": fecha,
            }

            self._boton_confirmar_ingreso.configure(state="disabled", text="Registrando...")

            def _on_resultado(resultado):
                exito, mensaje = resultado
                if exito:
                    popup.destroy()
                    self._mostrar_mensaje(mensaje, False)
                    self._refrescar_todo()
                else:
                    etiqueta_error_popup.configure(text=mensaje)
                    self._boton_confirmar_ingreso.configure(state="normal", text="✓ Registrar Ingreso")

            ejecutar_en_hilo(
                popup,
                tarea=lambda: self.controlador.registrar_ingreso(datos),
                callback_exito=_on_resultado,
                callback_error=lambda e: (
                    etiqueta_error_popup.configure(text=str(e)),
                    self._boton_confirmar_ingreso.configure(state="normal", text="✓ Registrar Ingreso"),
                ),
            )

        self._boton_confirmar_ingreso.configure(command=_confirmar_ingreso)
        entrada_busqueda.focus_set()

    # ══════════════════════════════════════════════════════════════════
    #  POPUP: CONFIRMAR EGRESO (DAR DE ALTA)
    # ══════════════════════════════════════════════════════════════════

    def _abrir_popup_egreso(self, ingreso):
        """Abre un popup para confirmar el egreso (dar de alta) de un paciente.

        Args:
            ingreso: IngresoDetalle del paciente a egresar.
        """
        popup = ctk.CTkToplevel(self)
        popup.title("Dar de Alta")
        popup.geometry("460x370")
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.configure(fg_color=self.C_FONDO)

        # Centrar
        popup.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 460) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 370) // 2
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            popup, text="Dar de Alta",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_SUBTITULO, weight="bold"),
            text_color=self.C_TEXTO,
        ).pack(padx=20, pady=(16, 10))

        # Info del paciente
        marco_info = ctk.CTkFrame(popup, fg_color=self.C_PANEL, corner_radius=8)
        marco_info.pack(fill="x", padx=20, pady=(0, 10))

        dias = self._calcular_dias_ingreso(ingreso.fecha_ingreso)
        info_lineas = [
            ("Paciente:", ingreso.nombre_completo),
            ("Cédula:", ingreso.cedula),
            ("N° Historia:", ingreso.num_historia),
            ("Fecha Ingreso:", ingreso.fecha_ingreso),
            ("Días ingresado:", f"{dias} día{'s' if dias != 1 else ''}"),
        ]
        for etiqueta_txt, valor_txt in info_lineas:
            fila = ctk.CTkFrame(marco_info, fg_color="transparent")
            fila.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(
                fila, text=etiqueta_txt, width=120,
                font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
                text_color=self.C_TEXTO_SEC, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                fila, text=valor_txt,
                font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA, weight="bold"),
                text_color=self.C_TEXTO, anchor="w",
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            popup, text="¿Desea dar de alta a este paciente?",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            text_color=self.C_TEXTO,
        ).pack(pady=(6, 4))

        etiqueta_error_egreso = ctk.CTkLabel(
            popup, text="", height=18,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_ERROR,
        )
        etiqueta_error_egreso.pack(fill="x", padx=20)

        marco_botones = ctk.CTkFrame(popup, fg_color="transparent")
        marco_botones.pack(fill="x", padx=20, pady=(6, 16))

        def _confirmar_egreso():
            def _on_resultado(resultado):
                exito, mensaje = resultado
                if exito:
                    popup.destroy()
                    self._mostrar_mensaje(mensaje, False)
                    self._refrescar_todo()
                else:
                    etiqueta_error_egreso.configure(text=mensaje)

            ejecutar_en_hilo(
                popup,
                tarea=lambda: self.controlador.registrar_egreso(ingreso.id),
                callback_exito=_on_resultado,
                callback_error=lambda e: etiqueta_error_egreso.configure(text=str(e)),
            )

        ctk.CTkButton(
            marco_botones, text="Dar de Alta", width=120,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            fg_color=self.C_PELIGRO, hover_color=self.C_PELIGRO_HOVER,
            text_color="#FFFFFF", corner_radius=6,
            command=_confirmar_egreso,
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            marco_botones, text="Cancelar", width=100,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            fg_color=self.C_ENTRADA, hover_color=self.C_BORDE,
            text_color=self.C_TEXTO, corner_radius=6,
            command=popup.destroy,
        ).pack(side="right")

    # ══════════════════════════════════════════════════════════════════
    #  POPUP: EDITAR CAPACIDAD DE CAMAS
    # ══════════════════════════════════════════════════════════════════

    def _abrir_popup_editar_camas(self):
        """Abre un popup modal para editar la capacidad de camas del servicio seleccionado."""
        if self.servicio_seleccionado is None:
            self._mostrar_mensaje("Seleccione un servicio primero.", True)
            return

        resumen = self._resumen_actual
        if not resumen:
            return
        servicio = resumen["servicio"]

        popup = ctk.CTkToplevel(self)
        popup.title(f"Editar Capacidad — {servicio.nombre}")
        popup.geometry("350x220")
        popup.resizable(False, False)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.configure(fg_color=self.C_FONDO)

        # Centrar
        popup.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 350) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 220) // 2
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            popup, text=f"Editar Capacidad — {servicio.nombre}",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_SUBTITULO, weight="bold"),
            text_color=self.C_TEXTO,
        ).pack(padx=20, pady=(16, 6))

        ctk.CTkLabel(
            popup, text=f"Ocupadas: {resumen['ocupadas']} / Actual: {servicio.total_camas}",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_TEXTO_SEC,
        ).pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(
            popup, text="Nuevo total de camas:",
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_TEXTO_SEC, anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 2))

        entrada_camas = ctk.CTkEntry(
            popup, placeholder_text=str(servicio.total_camas),
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            fg_color=self.C_ENTRADA, border_color=self.C_BORDE,
            text_color=self.C_TEXTO, height=34,
        )
        entrada_camas.pack(fill="x", padx=20, pady=(0, 6))
        entrada_camas.insert(0, str(servicio.total_camas))

        etiqueta_error_camas = ctk.CTkLabel(
            popup, text="", height=18,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_ETIQUETA),
            text_color=self.C_ERROR,
        )
        etiqueta_error_camas.pack(fill="x", padx=20)

        marco_botones = ctk.CTkFrame(popup, fg_color="transparent")
        marco_botones.pack(fill="x", padx=20, pady=(6, 16))

        def _guardar_camas():
            try:
                nuevo_total = int(entrada_camas.get().strip())
            except ValueError:
                etiqueta_error_camas.configure(text="Ingrese un número válido.")
                return

            id_serv = servicio.id

            def _on_resultado(resultado):
                exito, mensaje = resultado
                if exito:
                    popup.destroy()
                    self._mostrar_mensaje(mensaje, False)
                    self._refrescar_todo()
                else:
                    etiqueta_error_camas.configure(text=mensaje)

            ejecutar_en_hilo(
                popup,
                tarea=lambda: self.controlador.actualizar_camas_servicio(id_serv, nuevo_total),
                callback_exito=_on_resultado,
                callback_error=lambda e: etiqueta_error_camas.configure(text=str(e)),
            )

        ctk.CTkButton(
            marco_botones, text="Guardar", width=100,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            fg_color=self.C_ACENTO, hover_color=self.C_ACENTO_HOVER,
            text_color="#FFFFFF", corner_radius=6,
            command=_guardar_camas,
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            marco_botones, text="Cancelar", width=100,
            font=ctk.CTkFont(family="Segoe UI", size=self.F_BASE),
            fg_color=self.C_ENTRADA, hover_color=self.C_BORDE,
            text_color=self.C_TEXTO, corner_radius=6,
            command=popup.destroy,
        ).pack(side="right")

    # ══════════════════════════════════════════════════════════════════
    #  CAMBIO DE MODO VISTA
    # ══════════════════════════════════════════════════════════════════

    def _al_cambiar_modo_vista(self, valor):
        """Cambia entre modo galería y modo lista."""
        self.modo_vista = "galeria" if "Galería" in valor else "lista"
        if self.servicio_seleccionado is not None:
            self._cargar_contenido_servicio(self.servicio_seleccionado)

    # ══════════════════════════════════════════════════════════════════
    #  UTILIDADES
    # ══════════════════════════════════════════════════════════════════

    def _limpiar_contenido(self):
        """Destruye todos los widgets del contenido principal."""
        self.contenido_scroll.unbind("<Configure>")
        for widget in self.contenido_scroll.winfo_children():
            widget.destroy()
        self._widgets_contenido.clear()
        # Resetear columnas
        for i in range(10):
            self.contenido_scroll.grid_columnconfigure(i, weight=0)

    def _refrescar_todo(self):
        """Recarga servicios y contenido del servicio seleccionado."""
        ejecutar_en_hilo(
            self,
            tarea=self.controlador.obtener_resumen_general,
            callback_exito=self._on_refresco_servicios,
            callback_error=lambda e: self._mostrar_mensaje(f"Error: {e}", True),
        )

    def _on_refresco_servicios(self, resumenes):
        """Callback: actualiza el panel lateral y recarga el servicio actual."""
        self._resumen_servicios = resumenes
        self._renderizar_panel_servicios()
        if self.servicio_seleccionado is not None:
            self._cargar_contenido_servicio(self.servicio_seleccionado)

    def _calcular_dias_ingreso(self, fecha_str):
        """Calcula los días transcurridos desde la fecha de ingreso.

        Args:
            fecha_str: Fecha en formato DD-MM-AAAA, DD/MM/AAAA o YYYY-MM-DD.

        Returns:
            Número de días desde el ingreso.
        """
        try:
            fecha = parse_date(fecha_str)
            delta = datetime.datetime.now().date() - fecha
            return max(0, delta.days)
        except (ValueError, TypeError):
            return 0

    def _mostrar_mensaje(self, texto, es_error=False):
        """Muestra un mensaje en la barra inferior.

        Args:
            texto:    Texto del mensaje.
            es_error: True para mostrar en rojo, False para verde.
        """
        color = self.C_ERROR if es_error else self.C_EXITO
        self.etiqueta_mensaje.configure(text=texto, text_color=color)
        self.after(5000, lambda: self.etiqueta_mensaje.configure(text=""))
