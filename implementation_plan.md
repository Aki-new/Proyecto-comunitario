# Desarrollo Completo de Módulos — Sistema de Gestión Hospitalaria

## Contexto

El sistema ya cuenta con la arquitectura MVC básica (Models, DAOs, Controllers, Views) y un flujo funcional Login → Dashboard. Ahora se requiere:

1. **Reestructurar el manejo de colores y número de historia** según la lógica del hospital.
2. **Construir todos los módulos** del dashboard (Pacientes, Tarjetas, Búsqueda, Colores, Usuarios).

---

## Regla de Negocio: Número de Historia y Colores

### Formato del Número de Historia

El número de historia sigue el patrón `XX-XX-XX` (3 pares de dígitos separados por guiones):
- Cada par es un número de **máximo 2 dígitos** (00–99).
- Ejemplo válido: `03-77-34`.

### Color Auto-derivado del Último Par

El **último par de dígitos** determina automáticamente el color de la tarjeta, según la decena:

| Último par | Color         | Hex sugerido |
|------------|---------------|--------------|
| 00–09      | Marrón        | `#8B4513`    |
| 10–19      | Azul Marino   | `#000080`    |
| 20–29      | Verde         | `#228B22`    |
| 30–39      | Naranja       | `#FF8C00`    |
| 40–49      | Morado        | `#800080`    |
| 50–59      | Rosa          | `#FF69B4`    |
| 60–69      | Turquesa      | `#40E0D0`    |
| 70–79      | Amarillo      | `#FFD700`    |
| 80–89      | Rojo          | `#DC143C`    |
| 90–99      | Azul Celeste  | `#87CEEB`    |

> [!IMPORTANT]
> El color **ya no se selecciona manualmente**. Se calcula automáticamente al ingresar el número de historia. Esto elimina la necesidad del campo `id_color` como selección del usuario.

---

## Proposed Changes

### Componente 1: Modelos Pydantic

#### [MODIFY] [tarjeta.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/tarjeta.py)
- Agregar validador Pydantic `@field_validator` en `num_historia` para validar formato `XX-XX-XX`.
- Eliminar `id_color` de `TarjetaCreate` (se auto-deriva).
- Agregar método/propiedad para calcular el color desde `num_historia`.

#### [MODIFY] [color.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/models/color.py)
- Agregar campo `hex_color` al modelo para el código hexadecimal.
- Agregar campo `rango_inicio` y `rango_fin` para la lógica de rangos.

#### [NEW] src/models/num_historia_utils.py
- Función `validar_formato_num_historia(valor: str) -> bool`.
- Función `obtener_color_por_num_historia(num_historia: str) -> dict` que retorna `{"nombre": "...", "hex": "..."}`.
- Constante `MAPA_COLORES` con la tabla de decenas → color.

---

### Componente 2: Base de Datos y DAOs

#### [MODIFY] [schema.sql](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/database/schema.sql) (datos)
- No se modifica el esquema, pero el seed actualizará la tabla `colores` con los 10 colores correctos del hospital.

#### [MODIFY] [seed.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/seed.py)
- Reemplazar los colores actuales (Rojo, Azul, Verde, Amarillo, Blanco) por los 10 colores reales del hospital.
- Actualizar las tarjetas de prueba con números de historia en formato `XX-XX-XX`.

#### [MODIFY] [tarjeta.py (DAO)](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/dao/tarjeta.py)
- Modificar `crear()` para auto-calcular `id_color` a partir de `num_historia`.
- Agregar método `obtener_todos()` para listar tarjetas activas.

---

### Componente 3: Controladores

#### [MODIFY] [paciente_controller.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/controllers/paciente_controller.py)
- Ajustar `registrar_paciente_con_tarjeta()` para auto-derivar color.

#### [NEW] src/controllers/tarjeta_controller.py
- CRUD de tarjetas con validación de formato `XX-XX-XX`.
- Auto-derivación de color al crear/actualizar.

#### [NEW] src/controllers/busqueda_controller.py
- Búsqueda por cédula, nombre, apellido, número de historia.
- Retorno de resultados formateados para la tabla.

#### [NEW] src/controllers/usuario_controller.py
- CRUD de usuarios con validación Pydantic.

#### [NEW] src/controllers/color_controller.py
- Listar colores (solo lectura, son fijos).

---

### Componente 4: Vistas (Módulos del Dashboard)

Cada módulo es un `CTkFrame` que se carga dentro del `contenedor_pagina` del dashboard.

#### [NEW] src/views/pacientes_view.py
- **Tabla** con lista de pacientes activos (CTkScrollableFrame con filas).
- **Formulario** de registro/edición con todos los campos.
- Botones: Nuevo, Editar, Desactivar, Limpiar.
- Búsqueda rápida por cédula.

#### [NEW] src/views/tarjetas_view.py
- **Tabla** con tarjetas activas mostrando: Nº Historia, Paciente, Color (con indicador visual).
- **Formulario** para crear tarjeta: seleccionar paciente + ingresar `num_historia`.
- El color se muestra **automáticamente** al escribir el número de historia (preview en tiempo real).
- Validación visual del formato `XX-XX-XX`.

#### [NEW] src/views/busqueda_view.py
- Campo de búsqueda con filtro por tipo (cédula, nombre, apellido, Nº historia).
- **Tabla de resultados** con datos combinados de la vista SQL.
- Información detallada con color visual.

#### [NEW] src/views/colores_view.py
- Tabla de referencia (solo lectura) mostrando los 10 colores con:
  - Rango de números (00–09, 10–19, etc.).
  - Nombre del color.
  - Muestra visual del color (cuadrado con el hex).

#### [NEW] src/views/usuarios_view.py
- **Tabla** de usuarios activos.
- **Formulario** de registro/edición.
- Botones: Nuevo, Editar, Desactivar.

#### [MODIFY] [dashboard_view.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/views/dashboard_view.py)
- Conectar cada botón del menú lateral con su módulo correspondiente.
- Instanciar las vistas dentro de `contenedor_pagina` al navegar.

---

## Open Questions

> [!IMPORTANT]
> **¿El número de historia es editable después de crearlo?** Si se edita, el color cambiaría automáticamente. ¿Es correcto?

> [!IMPORTANT]
> **¿Un paciente puede tener múltiples tarjetas?** Actualmente la relación es 1:N en el schema (un paciente puede tener varias tarjetas), pero ¿en la práctica cada paciente tiene solo una tarjeta activa?

---

## Verification Plan

### Automated Tests
- Ejecutar `python seed.py` para verificar los datos de prueba actualizados.
- Ejecutar `python main.py` y probar:
  - Login → Dashboard.
  - Navegar por todos los módulos.
  - Crear un paciente nuevo.
  - Crear una tarjeta con formato `XX-XX-XX` y verificar auto-color.
  - Buscar por cédula/nombre/historia.
  - Gestionar usuarios.

### Manual Verification
- Verificar que el color se actualiza en tiempo real al escribir el número de historia.
- Verificar que los formatos inválidos son rechazados.
- Verificar que el soft-delete funciona en todos los módulos.
