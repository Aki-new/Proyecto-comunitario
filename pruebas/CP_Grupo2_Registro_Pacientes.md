REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-006
Caso de prueba:
Registro exitoso del paciente con tarjeta
Descripción del Caso:
Verificar que el paciente y su tarjeta clínica asociada sean agregados en la base de datos del sistema de forma exitosa
Precondición:
El paciente no debe estar registrado en la base de datos del sistema (cédula y número de historia no deben existir previamente).
Datos de prueba:
Cédula: V-27845612, Primer Nombre: Carlos, Segundo Nombre: José, Primer Apellido: Mendoza, Segundo Apellido: Rojas, Fecha de Nacimiento: 12/08/1995, Lugar de Nacimiento: Barquisimeto, Estado Vital: Vivo, Nº Historia: 10-25-34
Pasos a seguir:
1. Acceder al módulo de Pacientes en el Dashboard y hacer clic en "+ Nuevo Ingreso".
2. Seleccionar el tipo de cédula "V-" en el selector e ingresar el número "27845612" en el campo correspondiente.
3. Rellenar los campos obligatorios del paciente (Primer Nombre: Carlos, Primer Apellido: Mendoza, Lugar de Nacimiento: Barquisimeto, Fecha Nacimiento: 12/08/1995).
4. Escribir los nombres y apellidos opcionales si aplica (Segundo Nombre: José, Segundo Apellido: Rojas).
5. En la sección "TARJETA ÍNDICE", ingresar el número de historia "10-25-34".
6. Visualizar el color previsualizado en vivo (debe mostrar color Naranja según la regla de la decena '3').
7. Hacer clic en el botón "Guardar".
Resultado esperado:
El sistema registra al paciente y su tarjeta, limpia el formulario lateral y muestra un mensaje de éxito indicando que el paciente y su tarjeta se agregaron correctamente a la base de datos.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-007
Caso de prueba:
Registro exitoso de paciente menor de edad sin cédula ("S/C")
Descripción del Caso:
Verificar que el sistema permita el registro de pacientes infantiles que no poseen documento de identidad, guardando el valor de cédula como "S/C" (NULL en base de datos)
Precondición:
El número de historia clínica asignado al menor no debe estar registrado en el sistema.
Datos de prueba:
Cédula: S/C, Primer Nombre: Luis, Primer Apellido: Giménez, Fecha de Nacimiento: 05/10/2018, Lugar de Nacimiento: Cabudare, Estado Vital: Vivo, Nº Historia: 04-12-88
Pasos a seguir:
1. Acceder al módulo de Pacientes en el Dashboard y hacer clic en "+ Nuevo Ingreso".
2. En el desplegable de tipo de cédula, seleccionar la opción "S/C".
3. Verificar que el campo numérico de cédula se desactiva.
4. Rellenar los campos obligatorios (Primer Nombre: Luis, Primer Apellido: Giménez, Lugar de Nacimiento: Cabudare, Fecha Nacimiento: 05/10/2018).
5. En la sección "TARJETA ÍNDICE", ingresar el número de historia "04-12-88" (Color derivado: Rojo, decena 8).
6. Hacer clic en el botón "Guardar".
Resultado esperado:
El sistema procesa correctamente el registro. Se guarda el paciente con la cédula "S/C" en la base de datos (con valor NULL) y su tarjeta correspondiente de color Rojo.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-008
Caso de prueba:
Registro fallido - Cédula ya registrada (cédula duplicada)
Descripción del Caso:
Verificar que el sistema impida registrar a un paciente si su número de cédula de identidad ya se encuentra asignado a otro registro activo
Precondición:
Debe existir en el sistema un paciente con la cédula V-17795502.
Datos de prueba:
Cédula: V-17795502, Primer Nombre: Clara, Primer Apellido: Torres, Fecha de Nacimiento: 04/04/1990, Lugar de Nacimiento: Duaca, Nº Historia: 05-44-12
Pasos a seguir:
1. Acceder al módulo de Pacientes y hacer clic en "+ Nuevo Ingreso".
2. Seleccionar "V-" e ingresar la cédula duplicada: "17795502".
3. Rellenar los campos restantes con datos válidos.
4. Ingresar un número de historia no duplicado (ej: 05-44-12).
5. Hacer clic en "Guardar".
Resultado esperado:
El sistema deniega el registro, mostrando un mensaje de alerta en la interfaz indicando que la cédula ingresada ya está registrada en la base de datos.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-009
Caso de prueba:
Registro fallido - Formato de cédula incorrecto
Descripción del Caso:
Verificar que la validación del modelo Paciente impida el envío de una cédula con formato inválido
Precondición:
Ninguna
Datos de prueba:
Cédula ingresada: V-123 (menos de 6 dígitos) o 25412345 (sin guión inicial de tipo)
Pasos a seguir:
1. Acceder al módulo de Pacientes y hacer clic en "+ Nuevo Ingreso".
2. Seleccionar "V-" e ingresar "123" en la caja de texto de cédula.
3. Rellenar los demás campos con datos válidos.
4. Hacer clic en "Guardar".
Resultado esperado:
La validación Pydantic del modelo falla. El sistema muestra un mensaje de error detallado: "Formato de cédula inválido. Use V-12345678 o E-12345678 (6 a 10 dígitos)."
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-010
Caso de prueba:
Registro fallido - Número de historia clínica duplicado
Descripción del Caso:
Verificar que el sistema no permita registrar una tarjeta cuyo número de historia clínica (num_historia) ya exista en el sistema
Precondición:
Debe existir en el sistema una tarjeta con el número de historia 03-77-34.
Datos de prueba:
Cédula: V-28111222, Nombres y Apellidos válidos, Nº Historia: 03-77-34
Pasos a seguir:
1. Acceder al formulario de "+ Nuevo Ingreso".
2. Registrar una cédula y datos personales válidos.
3. En el número de historia, escribir "03-77-34" (número ya existente en la base de datos).
4. Hacer clic en "Guardar".
Resultado esperado:
El sistema deniega el registro de la tarjeta e informa a través de un mensaje en la interfaz que el número de historia clínica ya se encuentra registrado.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-011
Caso de prueba:
Registro fallido - Formato de número de historia incorrecto
Descripción del Caso:
Verificar que la validación impida registrar una historia clínica si no cumple con la regla de tres pares de dígitos separados por guiones
Precondición:
Ninguna
Datos de prueba:
Nº Historia: 123-456 (formato no válido), o 123456 (sin guiones), o AA-BB-CC (letras)
Pasos a seguir:
1. Abrir el formulario de "+ Nuevo Ingreso" y rellenar los datos del paciente válidamente.
2. En el campo de Nº Historia, escribir "12-345-6" o "A1-B2-C3".
3. Observar la previsualización del color (debe advertir un formato inválido).
4. Hacer clic en "Guardar".
Resultado esperado:
El sistema bloquea la transacción y muestra el mensaje de error: "El número de historia debe tener formato XX-XX-XX (3 pares de dígitos)".
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-012
Caso de prueba:
Registro fallido - Formato de fecha de nacimiento incorrecto
Descripción del Caso:
Verificar que la validación del modelo Paciente impida almacenar fechas de nacimiento lógicamente imposibles o en formatos incorrectos
Precondición:
Ninguna
Datos de prueba:
Fecha de nacimiento: 31/13/2010 (mes inexistente) o 32/05/2004 (día inválido) o 15-05-1899 (año fuera de rango 1900-2100)
Pasos a seguir:
1. Abrir el formulario de "+ Nuevo Ingreso".
2. Llenar los datos personales del paciente.
3. En la Fecha de Nacimiento, ingresar "31/13/2010".
4. Completar con un número de historia válido y presionar "Guardar".
Resultado esperado:
El sistema interrumpe el registro del paciente mostrando en rojo el error correspondiente de validación lógica de fecha (ej: "Mes inválido (debe ser 01-12).").
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-013
Caso de prueba:
Registro fallido - Campos obligatorios vacíos
Descripción del Caso:
Verificar que el sistema rechace el formulario de registro si alguno de los campos requeridos está vacío o contiene sólo espacios
Precondición:
Ninguna
Datos de prueba:
Primer Nombre: " " (espacios en blanco), Primer Apellido: "", Lugar de Nacimiento: ""
Pasos a seguir:
1. Abrir el formulario de "+ Nuevo Ingreso".
2. Dejar el campo Primer Nombre vacío o con espacios.
3. Rellenar los campos de cédula y fecha con datos válidos, y un número de historia válido.
4. Hacer clic en "Guardar".
Resultado esperado:
El sistema detecta la ausencia de datos en los campos requeridos y muestra un mensaje de error indicando: "Este campo es obligatorio" u "El lugar de nacimiento es obligatorio".
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)
