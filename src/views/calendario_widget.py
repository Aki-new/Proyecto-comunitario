"""Widgets de calendario para seleccion de fechas.

Contiene dos componentes reutilizables de CustomTkinter:

- **CalendarioPopup**: ventana emergente con grilla mensual para elegir un dia.
- **CampoFecha**: campo de entrada de texto con boton que despliega el popup.

Uso tipico::

    campo = CampoFecha(parent, tema=mi_tema)
    campo.pack(fill="x")
    fecha = campo.obtener_fecha()  # "25/05/2026"
"""

import calendar
import datetime

import customtkinter as ctk


# ==============================================================================
#  Constantes por defecto
# ==============================================================================

_COLORES_POR_DEFECTO = {
    "fondo": "#1E3044",
    "panel": "#182633",
    "acento": "#00A8E8",
    "texto": "#E8EDF2",
    "texto_secundario": "#8899AA",
    "entrada_fondo": "#1E3044",
    "entrada_borde": "#2A4158",
    "error": "#FF4C6A",
}

_FUENTE_TAMANOS_POR_DEFECTO = {
    "base": 13,
    "titulo": 16,
    "subtitulo": 14,
    "etiqueta": 12,
}

_NOMBRES_MESES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

_NOMBRES_DIAS = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]


# ==============================================================================
#  CalendarioPopup
# ==============================================================================


class CalendarioPopup(ctk.CTkToplevel):
    """Ventana emergente de calendario mensual para seleccion de fecha.

    Muestra una grilla de 7 columnas (Lun–Dom) por hasta 6 filas con los
    dias del mes actual.  Permite navegar entre meses con botones de
    flecha y seleccionar un dia haciendo clic sobre el.

    Parametros
    ----------
    parent : widget
        Widget padre; el popup se posiciona relativo a el.
    callback : callable
        Funcion que recibe un ``str`` con formato ``DD/MM/AAAA`` cuando
        el usuario selecciona un dia.
    tema : dict, opcional
        Diccionario con claves de color (``fondo``, ``panel``, ``acento``,
        ``texto``, ``texto_secundario``, ``entrada_fondo``, ``entrada_borde``).
        Si es ``None`` se usan los colores por defecto.
    fuente_tamano : dict, opcional
        Diccionario con claves ``base``, ``titulo``, ``subtitulo``,
        ``etiqueta`` indicando tamaños de fuente.  Si es ``None`` se usan
        los tamaños por defecto.
    """

    def __init__(self, parent, callback, tema=None, fuente_tamano=None):
        super().__init__(parent)

        # -- Configuracion de ventana ------------------------------------------
        self.wm_overrideredirect(True)
        self.transient(parent)
        self.grab_set()

        # -- Parametros --------------------------------------------------------
        self._callback = callback
        self._colores = {**_COLORES_POR_DEFECTO, **(tema or {})}
        self._fuentes = {**_FUENTE_TAMANOS_POR_DEFECTO, **(fuente_tamano or {})}

        # -- Estado del calendario ---------------------------------------------
        hoy = datetime.date.today()
        self._anio_actual = hoy.year
        self._mes_actual = hoy.month
        self._dia_hoy = hoy

        # -- Construir interfaz ------------------------------------------------
        self.configure(fg_color=self._colores["panel"])

        self._crear_encabezado()
        self._crear_fila_nombres_dias()
        self._crear_grilla_dias()
        self._renderizar_mes()

        # -- Posicionar cerca del widget padre ---------------------------------
        self._posicionar_popup(parent)

        # -- Cerrar al perder foco ---------------------------------------------
        self.bind("<FocusOut>", self._al_perder_foco)

    # ==========================================================================
    #  Construccion de la interfaz
    # ==========================================================================

    def _crear_encabezado(self):
        """Crea la barra de navegacion: « ← [Mes Año] → » y boton de cerrar.

        Botones: « retrocede un año, ← retrocede un mes,
        → avanza un mes, » avanza un año, y un boton ✕ para cerrar el popup.
        Los años van en los bordes externos y los meses en los internos.
        """
        marco_encabezado = ctk.CTkFrame(
            self,
            fg_color=self._colores["panel"],
            corner_radius=0,
        )
        marco_encabezado.pack(fill="x", padx=8, pady=(8, 4))

        estilo_btn_nav = dict(
            height=28, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["base"], weight="bold"),
            fg_color=self._colores["entrada_fondo"],
            hover_color=self._colores["entrada_borde"],
            text_color=self._colores["texto"],
        )

        # Boton año anterior (borde externo izquierdo)
        ctk.CTkButton(
            marco_encabezado, text="«", width=28,
            command=self._anio_anterior, **estilo_btn_nav,
        ).pack(side="left", padx=(0, 2))

        # Boton mes anterior (borde interno izquierdo)
        ctk.CTkButton(
            marco_encabezado, text="←", width=28,
            command=self._mes_anterior, **estilo_btn_nav,
        ).pack(side="left", padx=(0, 4))

        # Boton cerrar (borde externo derecho)
        color_error = self._colores.get("error", "#FF4C6A")
        ctk.CTkButton(
            marco_encabezado, text="✕", width=24,
            command=self._cerrar_popup,
            height=28, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["base"], weight="bold"),
            fg_color=self._colores["entrada_fondo"],
            hover_color=color_error,
            text_color=self._colores["texto"],
        ).pack(side="right", padx=(6, 0))

        # Boton año siguiente (borde externo derecho antes del boton cerrar)
        ctk.CTkButton(
            marco_encabezado, text="»", width=28,
            command=self._anio_siguiente, **estilo_btn_nav,
        ).pack(side="right", padx=(2, 0))

        # Boton mes siguiente (borde interno derecho)
        ctk.CTkButton(
            marco_encabezado, text="→", width=28,
            command=self._mes_siguiente, **estilo_btn_nav,
        ).pack(side="right", padx=(4, 0))

        # Etiqueta de mes y anio (centro)
        self.etiqueta_mes_anio = ctk.CTkLabel(
            marco_encabezado,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["subtitulo"], weight="bold"),
            text_color=self._colores["texto"],
        )
        self.etiqueta_mes_anio.pack(side="left", expand=True, padx=4)

    def _crear_fila_nombres_dias(self):
        """Crea la fila con los nombres abreviados de los dias de la semana."""
        marco_nombres = ctk.CTkFrame(
            self,
            fg_color=self._colores["entrada_fondo"],
            corner_radius=6,
        )
        marco_nombres.pack(fill="x", padx=8, pady=(0, 2))

        for nombre_dia in _NOMBRES_DIAS:
            ctk.CTkLabel(
                marco_nombres,
                text=nombre_dia,
                width=38,
                font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["etiqueta"], weight="bold"),
                text_color=self._colores["texto_secundario"],
            ).pack(side="left", expand=True, padx=1, pady=4)

    def _crear_grilla_dias(self):
        """Crea el contenedor de la grilla de dias (7 col × 6 filas max)."""
        self.marco_grilla_dias = ctk.CTkFrame(
            self,
            fg_color=self._colores["panel"],
            corner_radius=0,
        )
        self.marco_grilla_dias.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Configurar 7 columnas con peso uniforme
        for columna in range(7):
            self.marco_grilla_dias.grid_columnconfigure(columna, weight=1)

    # ==========================================================================
    #  Renderizado del mes
    # ==========================================================================

    def _renderizar_mes(self):
        """Dibuja los botones de dias para el mes y anio actuales.

        Limpia la grilla existente y la reconstruye con los dias del mes
        indicado por ``self._mes_actual`` y ``self._anio_actual``.
        Los dias del mes anterior y siguiente se muestran con color
        atenuado.  El dia de hoy se resalta con el color de acento.
        """
        # Limpiar grilla previa
        for widget_hijo in self.marco_grilla_dias.winfo_children():
            widget_hijo.destroy()

        # Actualizar etiqueta del encabezado
        nombre_mes = _NOMBRES_MESES[self._mes_actual - 1]
        self.etiqueta_mes_anio.configure(text=f"{nombre_mes} {self._anio_actual}")

        # Obtener la estructura del mes (semanas empezando en lunes)
        calendario = calendar.Calendar(firstweekday=0)  # 0 = Lunes
        semanas = calendario.monthdayscalendar(self._anio_actual, self._mes_actual)

        # Calcular dias del mes anterior para rellenar la primera semana
        if self._mes_actual == 1:
            mes_previo = 12
            anio_previo = self._anio_actual - 1
        else:
            mes_previo = self._mes_actual - 1
            anio_previo = self._anio_actual

        ultimo_dia_mes_previo = calendar.monthrange(anio_previo, mes_previo)[1]

        # Calcular dias del mes siguiente para rellenar la ultima semana
        if self._mes_actual == 12:
            mes_proximo = 1
            anio_proximo = self._anio_actual + 1
        else:
            mes_proximo = self._mes_actual + 1
            anio_proximo = self._anio_actual

        for indice_fila, semana in enumerate(semanas):
            # Contar ceros al inicio de la primera semana
            ceros_inicio = 0
            if indice_fila == 0:
                for dia_val in semana:
                    if dia_val == 0:
                        ceros_inicio += 1
                    else:
                        break

            contador_dia_siguiente = 1

            for indice_columna, dia in enumerate(semana):
                if dia == 0:
                    # Dia fuera del mes actual
                    if indice_fila == 0 and indice_columna < ceros_inicio:
                        # Dia del mes anterior
                        dia_mostrar = ultimo_dia_mes_previo - (ceros_inicio - 1 - indice_columna)
                        fecha_real = datetime.date(anio_previo, mes_previo, dia_mostrar)
                    else:
                        # Dia del mes siguiente
                        dia_mostrar = contador_dia_siguiente
                        contador_dia_siguiente += 1
                        fecha_real = datetime.date(anio_proximo, mes_proximo, dia_mostrar)

                    boton_dia = ctk.CTkButton(
                        self.marco_grilla_dias,
                        text=str(dia_mostrar),
                        width=36,
                        height=32,
                        corner_radius=6,
                        font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["etiqueta"]),
                        fg_color="transparent",
                        hover_color=self._colores["entrada_borde"],
                        text_color=self._colores["texto_secundario"],
                        command=lambda f=fecha_real: self._seleccionar_dia(f),
                    )
                else:
                    # Dia del mes actual
                    fecha_real = datetime.date(self._anio_actual, self._mes_actual, dia)
                    es_hoy = fecha_real == self._dia_hoy

                    color_fondo = self._colores["acento"] if es_hoy else "transparent"
                    color_texto = "#FFFFFF" if es_hoy else self._colores["texto"]
                    color_hover = self._colores["entrada_borde"] if not es_hoy else self._colores["acento"]

                    boton_dia = ctk.CTkButton(
                        self.marco_grilla_dias,
                        text=str(dia),
                        width=36,
                        height=32,
                        corner_radius=6,
                        font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["etiqueta"],
                                         weight="bold" if es_hoy else "normal"),
                        fg_color=color_fondo,
                        hover_color=color_hover,
                        text_color=color_texto,
                        command=lambda f=fecha_real: self._seleccionar_dia(f),
                    )

                boton_dia.grid(
                    row=indice_fila, column=indice_columna,
                    padx=1, pady=1, sticky="nsew",
                )

        # Asegurar que siempre hay 6 filas configuradas para tamano consistente
        for fila in range(6):
            self.marco_grilla_dias.grid_rowconfigure(fila, weight=1)

    # ==========================================================================
    #  Navegacion entre meses
    # ==========================================================================

    def _mes_anterior(self):
        """Retrocede un mes y redibuja la grilla."""
        if self._mes_actual == 1:
            self._mes_actual = 12
            self._anio_actual -= 1
        else:
            self._mes_actual -= 1
        self._renderizar_mes()

    def _mes_siguiente(self):
        """Avanza un mes y redibuja la grilla."""
        if self._mes_actual == 12:
            self._mes_actual = 1
            self._anio_actual += 1
        else:
            self._mes_actual += 1
        self._renderizar_mes()

    def _anio_anterior(self):
        """Retrocede un año y redibuja la grilla."""
        self._anio_actual -= 1
        self._renderizar_mes()

    def _anio_siguiente(self):
        """Avanza un año y redibuja la grilla."""
        self._anio_actual += 1
        self._renderizar_mes()

    # ==========================================================================
    #  Seleccion de dia
    # ==========================================================================

    def _seleccionar_dia(self, fecha: datetime.date):
        """Invoca el callback con la fecha formateada y cierra el popup.

        Parametros
        ----------
        fecha : datetime.date
            La fecha seleccionada por el usuario.
        """
        fecha_formateada = fecha.strftime("%d/%m/%Y")
        self._callback(fecha_formateada)
        self.grab_release()
        self.destroy()

    # ==========================================================================
    #  Posicionamiento y cierre
    # ==========================================================================

    def _posicionar_popup(self, widget_padre):
        """Coloca el popup justo debajo del widget padre.

        Calcula la posicion absoluta del widget padre en pantalla y situa
        la ventana emergente inmediatamente debajo.

        Parametros
        ----------
        widget_padre : widget
            El widget de referencia para posicionar el popup.
        """
        self.update_idletasks()

        # Obtener posicion absoluta del widget padre
        x_padre = widget_padre.winfo_rootx()
        y_padre = widget_padre.winfo_rooty()
        alto_padre = widget_padre.winfo_height()

        # Posicionar debajo del padre
        pos_x = x_padre
        pos_y = y_padre + alto_padre + 4

        # Ajustar si se sale de la pantalla
        ancho_popup = self.winfo_reqwidth()
        alto_popup = self.winfo_reqheight()
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()

        if pos_x + ancho_popup > ancho_pantalla:
            pos_x = ancho_pantalla - ancho_popup - 8

        if pos_y + alto_popup > alto_pantalla:
            # Mostrar arriba del padre en su lugar
            pos_y = y_padre - alto_popup - 4

        self.geometry(f"+{pos_x}+{pos_y}")

    def _cerrar_popup(self):
        """Cierra el popup liberando el grab de forma segura."""
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass

    def _al_perder_foco(self, evento=None):
        """Cierra el popup cuando pierde el foco del teclado.

        Se verifica que el foco no haya pasado a un widget hijo del
        propio popup (por ejemplo, un boton de dia) antes de destruirlo.

        Parametros
        ----------
        evento : tk.Event, opcional
            El evento de perdida de foco.
        """
        try:
            widget_con_foco = self.focus_get()
            # Si el foco se fue a un hijo del popup, no cerrar
            if widget_con_foco is not None:
                padre_del_foco = str(widget_con_foco)
                if str(self) in padre_del_foco:
                    return
        except Exception:
            pass

        self._cerrar_popup()


# ==============================================================================
#  CampoFecha
# ==============================================================================


class CampoFecha(ctk.CTkFrame):
    """Widget compuesto: campo de texto para fecha + boton de calendario.

    Combina un ``CTkEntry`` donde el usuario puede escribir manualmente
    una fecha en formato ``DD/MM/AAAA`` y un boton con icono de calendario
    (📅) que despliega un ``CalendarioPopup`` para seleccion visual.

    Parametros
    ----------
    parent : widget
        Widget padre.
    tema : dict, opcional
        Diccionario con claves de color.  Se pasa al ``CalendarioPopup``
        y se usa para estilizar la entrada y el boton.
    fuente_tamano : dict, opcional
        Diccionario con tamaños de fuente.  Se pasa al ``CalendarioPopup``.
    **kwargs
        Argumentos adicionales para ``CTkFrame``.

    Ejemplo
    -------
    >>> campo = CampoFecha(contenedor, tema={"acento": "#FF5500"})
    >>> campo.pack(fill="x", padx=16)
    >>> fecha = campo.obtener_fecha()
    >>> campo.establecer_fecha("01/01/2026")
    >>> campo.limpiar()
    """

    def __init__(self, parent, tema=None, fuente_tamano=None, **kwargs):
        # Resolver colores y fuentes
        self._colores = {**_COLORES_POR_DEFECTO, **(tema or {})}
        self._fuentes = {**_FUENTE_TAMANOS_POR_DEFECTO, **(fuente_tamano or {})}

        super().__init__(parent, fg_color="transparent", **kwargs)

        self._popup_abierto = False

        self._crear_widgets()

    # ==========================================================================
    #  Construccion de la interfaz
    # ==========================================================================

    def _crear_widgets(self):
        """Construye la entrada de texto y el boton de calendario."""
        # Campo de texto para la fecha
        self.entrada_fecha = ctk.CTkEntry(
            self,
            placeholder_text="DD/MM/AAAA",
            font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["base"]),
            fg_color=self._colores["entrada_fondo"],
            border_color=self._colores["entrada_borde"],
            text_color=self._colores["texto"],
            placeholder_text_color=self._colores["texto_secundario"],
            corner_radius=8,
            height=36,
        )
        self.entrada_fecha.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Boton para abrir el calendario
        self.boton_calendario = ctk.CTkButton(
            self,
            text="📅",
            width=36,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=self._fuentes["base"]),
            fg_color=self._colores["entrada_fondo"],
            hover_color=self._colores["entrada_borde"],
            text_color=self._colores["texto"],
            command=self._abrir_calendario,
        )
        self.boton_calendario.pack(side="right")

    # ==========================================================================
    #  Apertura del calendario
    # ==========================================================================

    def _abrir_calendario(self):
        """Despliega el popup de calendario debajo del boton.

        Evita abrir multiples instancias simultaneas del popup.
        """
        if self._popup_abierto:
            return

        self._popup_abierto = True

        popup = CalendarioPopup(
            parent=self.boton_calendario,
            callback=self._al_seleccionar_fecha,
            tema=self._colores,
            fuente_tamano=self._fuentes,
        )

        # Restablecer la bandera cuando se destruya el popup
        popup.bind("<Destroy>", self._al_cerrar_popup)

    def _al_seleccionar_fecha(self, fecha_str: str):
        """Callback invocado cuando el usuario selecciona una fecha en el popup.

        Llena la entrada de texto con la fecha seleccionada.

        Parametros
        ----------
        fecha_str : str
            Fecha en formato ``DD/MM/AAAA``.
        """
        self.entrada_fecha.delete(0, "end")
        self.entrada_fecha.insert(0, fecha_str)

    def _al_cerrar_popup(self, evento=None):
        """Restablece la bandera de popup abierto al destruirse.

        Parametros
        ----------
        evento : tk.Event, opcional
            El evento ``<Destroy>``.
        """
        self._popup_abierto = False

    # ==========================================================================
    #  Metodos publicos
    # ==========================================================================

    def obtener_fecha(self) -> str:
        """Retorna el texto actual del campo de fecha.

        Retorna
        -------
        str
            El contenido del campo de entrada, puede estar vacio o
            contener una fecha en formato ``DD/MM/AAAA``.
        """
        return self.entrada_fecha.get().strip()

    def establecer_fecha(self, fecha: str):
        """Establece el contenido del campo de fecha.

        Limpia cualquier contenido previo y coloca el nuevo valor.

        Parametros
        ----------
        fecha : str
            La fecha a establecer, preferiblemente en formato ``DD/MM/AAAA``.
        """
        self.entrada_fecha.delete(0, "end")
        self.entrada_fecha.insert(0, fecha)

    def limpiar(self):
        """Limpia el contenido del campo de fecha, dejandolo vacio."""
        self.entrada_fecha.delete(0, "end")
