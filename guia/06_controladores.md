# 🎮 Guía 6: Capa de Controladores y Orquestación de Negocio — SGI Salud

Esta guía describe el funcionamiento de los **Controladores** de SGI Salud, analizando cómo administran los flujos de trabajo, formatean los errores de validación de Pydantic y gestionan transacciones complejas de datos.

---

## 1. El Rol de los Controladores

Si la Vista es la cara de la aplicación y la base de datos es la memoria, el **Controlador es el cerebro**.
* **Coordinación**: Un controlador recibe datos en bruto del frontend (como diccionarios con strings), los procesa, los valida y los deriva al DAO correspondiente.
* **Aislamiento**: Evita que las pantallas gráficas interactúen con la base de datos de manera directa. Si una vista pudiese realizar consultas SQL, un error de base de datos podría romper la interfaz gráfica de forma catastrófica.

---

## 2. Gestión de Errores y Retorno de Respuestas Controladas

Los controladores de SGI Salud no lanzan excepciones hacia la interfaz gráfica. En su lugar, utilizan un patrón de **retornos de tupla estructurada**:
`(exito: bool, mensaje: str, [opcional] datos)`

### 2.1 Captura y Traducción de `ValidationError` de Pydantic
Cuando un usuario escribe datos erróneos en un formulario, Pydantic lanza una excepción estructurada `ValidationError` que contiene una jerarquía técnica en formato JSON. El controlador la captura de forma interna y la traduce a viñetas legibles por humanos usando el método auxiliar `_formatear_errores`:

```python
@staticmethod
def _formatear_errores(e: ValidationError) -> list[str]:
    errores = []
    for error in e.errors():
        # Obtiene la ruta física del campo con error
        campo = " -> ".join(str(loc) for loc in error["loc"])
        # Traduce o agrega el mensaje de validación correspondiente
        errores.append(f"  {campo}: {error['msg']}")
    return errores
```

### 2.2 Flujo Práctico de Validación
Si el usuario envía una fecha incorrecta como `"32/13/2026"`, la Vista llama a `registrar_paciente()`. El flujo es el siguiente:
1. El controlador ejecuta `paciente = PacienteCreate(**datos)`.
2. Pydantic detecta la fecha imposible y lanza `ValidationError`.
3. El controlador la captura con `except ValidationError as e`.
4. El método `_formatear_errores` compila la lista y el controlador retorna:
   `False, "Errores de validacion:\n  fecha_nacimiento: Mes invalido (debe ser 01-12).", None`
5. La vista recibe este `False`, salta al bloque visual de alerta y pinta el mensaje en letras rojas para el usuario, todo sin congelar el hilo de CustomTkinter.

---

## 3. Orquestación Atómica de Inserción: `registrar_paciente_con_tarjeta`

La operación más importante de la aplicación es registrar un paciente de forma conjunta con su tarjeta índice. Al ser dos tablas distintas en base de datos (`pacientes` y `tarjetas`), el controlador [paciente_controller.py](file:///c:/Users/Ruisu/OneDrive/Escritorio/ProyectoComunitario/src/controllers/paciente_controller.py#L53-L119) implementa una secuencia coordinada con múltiples validaciones previas para evitar inconsistencias:

```
                      ┌─────────────────────────────────┐
                      │    Datos Paciente + N. Historia │
                      └────────────────┬────────────────┘
                                       │
                      1. validar_formato_num_historia()
                                      / \
                                NO   /   \  SÍ
                                    /     \
                                   ▼       ▼
                          [Error Formato]  2. Validar Paciente con Pydantic
                                                  / \
                                            NO   /   \  SÍ
                                                /     \
                                               ▼       ▼
                                      [Error Datos]  3. ¿Existe cédula activa en DB?
                                                            / \
                                                      SÍ   /   \  NO
                                                          /     \
                                                         ▼       ▼
                                                  [Error Duplic.] 4. PacienteDAO.crear()
                                                                         │
                                                                   id_paciente
                                                                         │
                                                                         ▼
                                                     5. Derivar color del N. Historia
                                                     6. Buscar id_color en ColorDAO
                                                                         │
                                                                     id_color
                                                                         │
                                                                         ▼
                                                     7. TarjetaDAO.crear(id_paciente, id_color)
                                                                         │
                                                                     id_tarjeta
                                                                         │
                                                                         ▼
                                                             [REGISTRO EXITOSO]
```

### Detalle de Pasos de la Secuencia:
1. **Validación de Número de Historia**: Verifica que la cadena cumpla el patrón `XX-XX-XX` mediante utilidades de formato antes de tocar la base de datos.
2. **Validación de Datos del Paciente**: Valida tipos de datos, corrección de fechas y normaliza el campo cédula con `PacienteCreate`.
3. **Validación de Cédula Duplicada (Backend)**: Si el paciente tiene una cédula distinta de `"S/C"`, consulta con `PacienteDAO.obtener_por_cedula()`. Si ya existe otro paciente activo con esa identificación, aborta la operación con un error, evitando violaciones de lógica de negocio.
4. **Inserción de Paciente**: Llama a `PacienteDAO.crear()`. Si tiene éxito, el motor devuelve el ID de fila autogenerado (`id_paciente`).
5. **Derivación Automática de Color**: Ejecuta el algoritmo de decenas para descifrar el color (ej: `'34'` al final → `"Naranja"`).
6. **Resolución de ID de Color**: Consulta a `ColorDAO.obtener_por_valor("Naranja")` para obtener su ID correspondiente en base de datos.
7. **Inserción de Tarjeta**: Construye el objeto `TarjetaCreate` pasándole el `id_paciente` e `id_color` resueltos y los inserta en `TarjetaDAO.crear()`. Si el número de historia ya estaba asignado a otra persona en el hospital, el motor lanzará un error de unicidad, el DAO devolverá `-1` y el controlador cancelará la transacción informando que el número está duplicado.
