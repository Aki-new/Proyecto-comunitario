# 🎨 Guía 7: Capa de Interfaz Gráfica (Vistas) — SGI Salud

Esta guía analiza el funcionamiento de la **Capa de Vistas** de SGI Salud, detallando la biblioteca de componentes modernos **CustomTkinter**, el ciclo de vida de navegación, la lógica interactiva en caliente del formulario de pacientes y cómo desarrollar nuevos módulos visuales.

---

## 1. El Stack Gráfico: CustomTkinter

SGI Salud implementa **CustomTkinter** (`v5.2.2`) en lugar del Tkinter nativo tradicional de Python.
* **Modernidad Visual**: CustomTkinter provee soporte integrado de fábrica para esquemas de color dinámicos (Tema Oscuro por defecto en SGI Salud).
* **Componentes Premium**: Ofrece widgets estilizados con bordes redondeados, degradados y micro-animaciones en botones, entradas de texto (`CTkEntry`), desplegables (`CTkOptionMenu`) y contenedores con scroll (`CTkScrollableFrame`).
* **Tipografía**: Utiliza la fuente del sistema **Segoe UI** en Windows, adaptándose dinámicamente según la escala configurada por el operario.

---

## 2. Ciclo de Vida y Enrutamiento de Ventanas (`main.py`)

La gestión del paso de pantallas (de la ventana de Login al Panel Principal) no se maneja destruyendo y creando instancias aleatorias del sistema operativo. Se orquesta de forma controlada mediante callbacks en [main.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/main.py):

```
                        ┌───────────────────────────────┐
                        │           main.py             │
                        │   (Inicializa CTk() oculto)   │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │          LoginView            │
                        │    (Pide usuario y clave)     │
                        └───────────────┬───────────────┘
                                        │
                                 on_login_success
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │        DashboardView          │
                        │   (Menú lateral izquierdo)    │
                        └───────────────┬───────────────┘
                                        │
                                    on_logout
                                        │
                                        ▼
                               [Vuelve a LoginView]
```

### El Truco de la Raíz Oculta:
Para evitar que la aplicación se cierre al destruir la ventana de Login, `main.py` genera una ventana raíz master `self.root = ctk.CTk()` y ejecuta `self.root.withdraw()` (la oculta físicamente del monitor). 
* Tanto `LoginView` como `DashboardView` se crean como ventanas hijas (`ctk.CTkToplevel`) dependientes de esa raíz oculta.
* Cuando el usuario hace login con éxito, destruimos `LoginView` y abrimos `DashboardView`. La raíz master sigue viva en segundo plano controlando el `mainloop()`.

---

## 3. Lógica Interactiva en `PacientesView` (Módulo Crítico)

El archivo [pacientes_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/pacientes_view.py) contiene la pantalla más compleja de la aplicación. Implementa comportamientos dinámicos de nivel premium para agilizar la usabilidad:

### 3.1 Layout de Compresión Dinámica de Tabla
Para no obligar al usuario a navegar entre distintas ventanas para buscar o registrar, se unifica todo en una sola pantalla dividida en dos zonas mediante grid layout:
* **Estado Cerrado (Búsqueda/Lectura)**: La tabla de resultados ocupa el **100%** del ancho de la ventana.
* **Estado Abierto (Edición/Creación)**: Al pulsar `"+ Nuevo Ingreso"` o hacer doble clic sobre un paciente, la tabla de resultados se comprime dinámicamente ocupando el **55%** del ancho de la pantalla, abriendo a su derecha un panel de formulario lateral del **45%** de ancho.
* **Comportamiento**: Al pulsar el botón "Cerrar" del formulario, este se destruye y la tabla recupera automáticamente el 100% de la visualización mediante llamadas al método `.grid(row=0, column=0, columnspan=...)`.

### 3.2 Desactivación Inteligente de Cédulas ("S/C")
El formulario implementa un desplegable de selección de tipo de cédula: `"V-"`, `"E-"`, `"S/C"`.
* Si el operario selecciona `"V-"` o `"E-"`, el cuadro de texto numérico a su derecha se habilita (`state="normal"`) y cambia su color de fondo a un azul marino suave (`COLOR_ENTRY_BG`), invitando a escribir.
* Si el operario selecciona `"S/C"` (paciente sin cédula), el sistema ejecuta en caliente:
  ```python
  self.entry_cedula.delete(0, "end")       # Borra cualquier residuo numérico
  self.entry_cedula.configure(state="disabled") # Deshabilita la escritura
  ```
  Esto evita errores donde se guardaban por accidente números de cédula asociados al identificador "S/C".

### 3.3 Algoritmo de Previsualización de Color en Tiempo Real
Mientras el operario tipea los dígitos del número de historia clínica en el formulario, un evento en caliente (`.bind("<KeyRelease>")`) analiza la cadena de texto:

```python
def _on_historia_keyrelease(self, event):
    valor = self.entry_historia.get().strip()
    
    # 1. Comprobar si cumple con el patrón de formato básico XX-XX-XX
    if not validar_formato_num_historia(valor):
        self.label_preview_color.configure(text="Formato: XX-XX-XX", text_color=COLOR_ERROR)
        self.box_color_preview.configure(fg_color="transparent") # Oculta preview
        return
        
    # 2. Si es válido, extraer la decena del último par y buscar su color
    info_color = obtener_color_por_num_historia(valor)
    nombre_color = info_color["nombre"]
    hex_color = info_color["hex"]
    
    # 3. Actualizar la interfaz gráfica de forma reactiva
    self.label_preview_color.configure(text=f"Tarjeta: {nombre_color}", text_color=COLOR_TEXT)
    self.box_color_preview.configure(fg_color=hex_color) # Pinta el cuadro de color físico
```

* **Usabilidad**: El operario ve de forma instantánea si al tipear el número de historia, la tarjeta física correspondiente en el archivador debe ser roja, verde o morada, previniendo errores humanos de archivado antes de guardar la información.

---

## 4. ¿Cómo crear y registrar una nueva pantalla (Frame)?

Si deseas agregar un nuevo módulo a la aplicación (ejemplo: `AjustesView`), debes estructurarlo heredando de `ctk.CTkFrame`:

1. **Crear el Archivo**: Crea `src/views/ajustes_view.py`.
2. **Definir la Estructura**:
   ```python
   import customtkinter as ctk

   class AjustesView(ctk.CTkFrame):
       def __init__(self, master, controller, **kwargs):
           super().__init__(master, **kwargs)
           self.controller = controller
           
           # Inicializar interfaz gráfica y widgets del módulo
           self.label_titulo = ctk.CTkLabel(self, text="Configuración del Sistema")
           self.label_titulo.pack(pady=20)
   ```
3. **Enlazar en el Dashboard**: Abre [dashboard_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/dashboard_view.py):
   * Importa `AjustesView`.
   * Agrega un botón en el sidebar izquierdo: `"⚙️ Ajustes"`.
   * En el método selector de pantallas (`_cambiar_modulo()`), destruye el frame del módulo activo actual, instancia `AjustesView` pasándole `self.container` como master y ejecútalo mediante `.pack(fill="both", expand=True)`.
