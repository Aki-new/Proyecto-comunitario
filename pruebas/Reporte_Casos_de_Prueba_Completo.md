# REPORTE DE CASOS DE PRUEBA COMPLETO — SGI SALUD
**Hospital Dr. Armando Delgado Montero (DADM)**
**Sistema de Gestión de Información Estadística y Registros de Salud**

---

# GRUPO 1: AUTENTICACIÓN (LOGIN / LOGOUT)

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-001
Caso de prueba:
Inicio de Sesión exitoso
Descripción del Caso:
Verificar el inicio de sesión con credencial correcta
Precondición:
El usuario debe estar registrado en el sistema
Datos de prueba:
Usuario: Anaguedez@correo.com / Contraseña: 2215
Pasos a seguir:
1. Ingresar a la interfaz de inicio de sesión.
2. Escribir el usuario en el campo correspondiente.
3. Escribir la contraseña en el campo correspondiente.
4. Hacer Clic en el botón Ingresar.
Resultado esperado:
El sistema emite un mensaje de inicio de sesión exitoso y redirige al usuario a la sección de inicio mostrando un mensaje de bienvenida.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-002
Caso de prueba:
Inicio de Sesión fallido - Contraseña incorrecta
Descripción del Caso:
Verificar que el sistema impida el ingreso cuando se introduce una contraseña incorrecta para un usuario existente
Precondición:
El usuario debe estar registrado en el sistema
Datos de prueba:
Usuario: Anaguedez@correo.com / Contraseña: clave_erronea
Pasos a seguir:
1. Ingresar a la interfaz de inicio de sesión.
2. Escribir el usuario correcto en el campo correspondiente.
3. Escribir una contraseña incorrecta en el campo correspondiente.
4. Hacer Clic en el botón Ingresar.
Resultado esperado:
El sistema no permite el acceso y emite un mensaje de error destacando que las credenciales son incorrectas.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-003
Caso de prueba:
Inicio de Sesión fallido - Usuario inexistente
Descripción del Caso:
Verificar que el sistema impida el ingreso al ingresar un nombre de usuario que no está registrado en la base de datos
Precondición:
El usuario ingresado no debe estar registrado en el sistema
Datos de prueba:
Usuario: usuario_inexistente / Contraseña: cualquier_clave
Pasos a seguir:
1. Ingresar a la interfaz de inicio de sesión.
2. Escribir un usuario inexistente en el campo correspondiente.
3. Escribir cualquier contraseña en el campo correspondiente.
4. Hacer Clic en el botón Ingresar.
Resultado esperado:
El sistema deniega el acceso y muestra un mensaje de error indicando credenciales inválidas.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-004
Caso de prueba:
Inicio de Sesión fallido - Campos vacíos
Descripción del Caso:
Verificar que el sistema impida el inicio de sesión si alguno de los campos requeridos se deja en blanco
Precondición:
Ninguna
Datos de prueba:
Usuario: (Vacío) / Contraseña: (Vacío)
Pasos a seguir:
1. Ingresar a la interfaz de inicio de sesión.
2. Dejar el campo de usuario vacío.
3. Dejar el campo de contraseña vacío.
4. Hacer Clic en el botón Ingresar.
Resultado esperado:
El sistema no procesa la autenticación y muestra un mensaje de advertencia indicando que todos los campos son obligatorios.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-005
Caso de prueba:
Cierre de Sesión exitoso (Logout)
Descripción del Caso:
Verificar que el usuario pueda cerrar su sesión activa de forma segura y regresar a la pantalla de login
Precondición:
El usuario debe haber iniciado sesión y estar en el Dashboard principal
Datos de prueba:
Sesión iniciada
Pasos a seguir:
1. Ubicarse en el panel lateral del Dashboard.
2. Localizar el botón "Cerrar Sesión" (resaltado en color rojo).
3. Hacer clic en el botón "Cerrar Sesión".
Resultado esperado:
La sesión activa del usuario se destruye, la ventana principal se cierra o cambia, y se redirige al usuario a la interfaz de Inicio de Sesión (LoginView).
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

# GRUPO 2: REGISTRO DE PACIENTES Y TARJETAS ÍNDICE

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




---

# GRUPO 3: BÚSQUEDA DE PACIENTES (FILTROS DE BÚSQUEDA)

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-014
Caso de prueba:
Búsqueda de Paciente Por Nº de cédula de identidad completo
Descripción del Caso:
Verificar la correcta búsqueda ingresando el Nº de cédula completo del paciente
Precondición:
El paciente debe estar registrado en el sistema.
Datos de prueba:
Cédula: V-31284678
Pasos a seguir:
1. Acceder a la sección de búsqueda de pacientes en la barra superior.
2. Seleccionar la opción de filtro "Cédula" en el menú desplegable.
3. Ingresar el Nº de cédula "V-31284678" en el campo de texto de búsqueda.
4. Hacer clic en el botón "Buscar".
5. Visualizar la fila de resultado correspondiente en la tabla.
Resultado esperado:
El sistema muestra únicamente al paciente poseedor de la cédula ingresada en la tabla de resultados.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones / Comentarios:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-015
Caso de prueba:
Búsqueda de Paciente por número de cédula parcial o inexistente
Descripción del Caso:
Verificar el comportamiento del sistema cuando se ingresa una coincidencia parcial de cédula o una cédula que no existe
Precondición:
Ninguna
Datos de prueba:
Caso A (parcial): "284" / Caso B (inexistente): "V-99999999"
Pasos a seguir:
1. Ir a la barra de búsqueda de pacientes.
2. Seleccionar el filtro "Cédula".
3. Escribir "284" en el campo de búsqueda y hacer clic en "Buscar". Verificar coincidencias parciales.
4. Borrar la entrada, escribir "V-99999999" y hacer clic en "Buscar".
Resultado esperado:
Para el Caso A (parcial), el sistema lista en la tabla todos los pacientes cuya cédula contenga los dígitos "284".
Para el Caso B (inexistente), la tabla queda vacía y se muestra un mensaje "No se encontraron resultados" con un botón para registrar un nuevo paciente.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-016
Caso de prueba:
Busqueda de pacientes por Nombre completo
Descripción del Caso:
Verificar que se busquen correctamente los pacientes usando el filtro de su nombre completo
Precondición:
El paciente a buscar debe estar previamente registrado en el sistema.
Datos de prueba:
Nombre completo: María del Valle Palacios
Pasos a seguir:
1. En la barra de búsqueda de pacientes, seleccionar la opción "Nombre Completo" en el menú desplegable de criterios.
2. Ingresar el texto "María del Valle Palacios" en la casilla de búsqueda.
3. Iniciar la búsqueda haciendo clic en "Buscar".
4. Verificar la presencia del paciente esperado en los resultados de la tabla.
Resultado esperado:
Entre los resultados obtenidos debe estar el paciente: María del Valle Palacios, CI: 17.795.502, Lugar de nacimiento: Píritu, Fecha de nacimiento: 17/05/2002.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-017
Caso de prueba:
Búsqueda de paciente por primer o segundo apellido
Descripción del Caso:
Verificar que el sistema retorne los pacientes correctos al buscar empleando el filtro de apellido (coincidencia con primer o segundo apellido)
Precondición:
Deben existir registros con apellidos como "González" o "Rojas" en la base de datos.
Datos de prueba:
Apellido: González
Pasos a seguir:
1. Seleccionar la opción de filtro "Apellido" en el selector de la barra de búsqueda.
2. Escribir "González" en el campo de búsqueda.
3. Hacer clic en el botón "Buscar".
Resultado esperado:
El sistema muestra en la tabla todos los pacientes activos que tengan "González" como primer o segundo apellido.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-018
Caso de prueba:
Busqueda de paciente por fecha de nacimiento
Descripción del Caso:
Verificar que se busque correctamente los pacientes usando el filtro de fecha de nacimiento
Precondición:
Que haya al menos 1 paciente registrado con la fecha de nacimiento 19/06/1997.
Datos de prueba:
Fecha de nacimiento: 19/06/1997
Pasos a seguir:
1. Seleccionar el filtro "Fecha Nacimiento" en la barra de búsqueda.
2. Ingresar la fecha de nacimiento "19/06/1997" en la casilla correspondiente.
3. Iniciar la búsqueda.
4. Visualizar que haya al menos 1 paciente en la tabla que concuerde con la fecha de nacimiento ingresada.
Resultado esperado:
Que se muestre al menos 1 paciente con la fecha especificada en formato DD/MM/AAAA.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-019
Caso de prueba:
Búsqueda de paciente por lugar de nacimiento
Descripción del Caso:
Verificar que el sistema pueda filtrar y agrupar pacientes en base a su procedencia o lugar de nacimiento
Precondición:
Deben existir pacientes registrados de "Cabudare".
Datos de prueba:
Lugar de Nacimiento: Cabudare
Pasos a seguir:
1. Seleccionar el criterio de búsqueda "Lugar Nacimiento".
2. Escribir "Cabudare" en la barra de texto de búsqueda.
3. Presionar "Buscar".
Resultado esperado:
El sistema lista todos los pacientes cuyo lugar de nacimiento contenga la cadena de caracteres "Cabudare".
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-020
Caso de prueba:
Búsqueda general ("todos")
Descripción del Caso:
Verificar que al seleccionar el criterio general "Todos" y dejar el buscador vacío, el sistema liste la totalidad de pacientes activos
Precondición:
Deberían existir registros activos en la base de datos.
Datos de prueba:
Criterio: Todos / Texto: (Vacío)
Pasos a seguir:
1. Seleccionar el criterio de búsqueda "Todos".
2. Dejar el cuadro de búsqueda completamente vacío.
3. Hacer clic en "Buscar" (o recargar la sección).
Resultado esperado:
La tabla del módulo se pobla con la lista completa de todos los pacientes activos (con tarjeta) registrados en el sistema, ordenados por su ingreso o ID.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

# GRUPO 4: EDICIÓN Y DESACTIVACIÓN (BORRADO LÓGICO)

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-021
Caso de prueba:
Edición exitosa de datos personales de paciente
Descripción del Caso:
Verificar que al seleccionar un paciente en la lista y modificar sus datos personales, estos se guarden correctamente en la base de datos
Precondición:
El paciente debe estar previamente registrado (ej: Carlos Mendoza).
Datos de prueba:
ID Paciente: 5, Cambios: Lugar de Nacimiento -> Carora, Segundo Nombre -> Antonio
Pasos a seguir:
1. Buscar al paciente "Carlos Mendoza" en la tabla del módulo de Pacientes.
2. Hacer doble clic o un clic sobre la fila del paciente para cargar sus datos en el formulario lateral de edición.
3. Modificar el campo "Lugar de Nacimiento" a "Carora".
4. Modificar el campo "Segundo Nombre" a "Antonio".
5. Hacer clic en el botón "Guardar" (o "Actualizar").
Resultado esperado:
El sistema procesa la modificación, actualiza la base de datos, limpia el formulario lateral y emite un mensaje de éxito. Al volver a buscar al paciente, se reflejan sus datos actualizados.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-022
Caso de prueba:
Edición exitosa de número de historia clínica
Descripción del Caso:
Verificar que al cambiar el número de historia de un paciente, el sistema valide el formato, recalcule el color en base a la decena del último par del nuevo número y actualice la tarjeta
Precondición:
El paciente debe estar registrado con un número de historia inicial (ej: 10-25-34, color Naranja).
Datos de prueba:
Nuevo Nº Historia: 10-25-92 (El último par es 92, decena 9, corresponde a color Azul Celeste)
Pasos a seguir:
1. Buscar y seleccionar al paciente para cargar sus datos en el formulario.
2. Localizar el campo "N. Historia" e ingresar el nuevo valor "10-25-92".
3. Observar la previsualización del color (debe cambiar dinámicamente de Naranja a Azul Celeste).
4. Hacer clic en "Guardar".
Resultado esperado:
El sistema guarda el nuevo número de historia de la tarjeta y asocia el ID del color "Azul Celeste" en base de datos. Se muestra un mensaje de actualización exitosa.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-023
Caso de prueba:
Edición fallida - Intentar cambiar cédula por una ya existente
Descripción del Caso:
Verificar que no sea posible actualizar la cédula de un paciente con un número que ya pertenece a otro paciente registrado
Precondición:
Deben existir dos pacientes registrados en el sistema: Paciente A con cédula V-10000001 y Paciente B con cédula V-20000002.
Datos de prueba:
Editar Paciente B, cambiar su cédula a: V-10000001
Pasos a seguir:
1. Cargar los datos del Paciente B en el formulario lateral haciendo clic en su fila.
2. Cambiar la cédula del Paciente B por la del Paciente A ("10000001").
3. Hacer clic en "Guardar".
Resultado esperado:
El sistema cancela la actualización y muestra un mensaje de error advirtiendo que la cédula ya se encuentra en uso por otro paciente.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-024
Caso de prueba:
Edición fallida - Intentar cambiar número de historia por uno duplicado
Descripción del Caso:
Verificar que el sistema impida cambiar el número de historia de una tarjeta a un valor que ya está asignado a otra tarjeta activa
Precondición:
Tarjeta A tiene el Nº Historia 01-11-22. Tarjeta B tiene el Nº Historia 02-22-33.
Datos de prueba:
Editar Tarjeta B, cambiar número de historia a: 01-11-22
Pasos a seguir:
1. Seleccionar al paciente dueño de la Tarjeta B en la tabla para editar sus datos.
2. Modificar el campo "N. Historia" a "01-11-22" (duplicado).
3. Hacer clic en "Guardar".
Resultado esperado:
El sistema detiene la operación y muestra una alerta indicando que el número de historia clínica ingresado ya está asignado a otra tarjeta índice.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-025
Caso de prueba:
Desactivación lógica de paciente (Soft Delete)
Descripción del Caso:
Verificar que al "Eliminar" a un paciente, este deje de figurar en las búsquedas pero sus datos se mantengan en base de datos con estado = 0
Precondición:
El paciente debe existir y estar activo en el sistema.
Datos de prueba:
Paciente a eliminar (ej: Carlos Mendoza)
Pasos a seguir:
1. Seleccionar al paciente Carlos Mendoza en la tabla.
2. Hacer clic en el botón "Eliminar" (o "Desactivar") en el formulario/interfaz.
3. Confirmar la acción en el cuadro de diálogo emergente de confirmación.
4. Buscar nuevamente al paciente usando la barra de búsqueda (criterio "Todos" o "Cédula").
Resultado esperado:
El sistema notifica la eliminación exitosa del paciente. La tabla de búsqueda se actualiza y el paciente ya no aparece listado en ninguna vista de la interfaz gráfica.
En la base de datos SQLite, el registro mantiene su `id` pero el campo `estado` pasa a ser `0`.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

# GRUPO 5: SISTEMA DE COLORES (ASIGNACIÓN AUTOMÁTICA)

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-026
Caso de prueba:
Asignación automática de color según dígito decena del último par
Descripción del Caso:
Verificar que el sistema asocie y almacene el color de tarjeta correcto basándose exclusivamente en el primer dígito del último par (decena) del número de historia clínica
Precondición:
Tener acceso a la pantalla de "+ Nuevo Ingreso" en el módulo de Pacientes.
Datos de prueba:
Varios formatos de prueba:
1. Historia: 12-34-05 -> Par final: 05 -> Decena: 0 -> Color esperado: Marrón
2. Historia: 99-88-23 -> Par final: 23 -> Decena: 2 -> Color esperado: Verde
3. Historia: 00-00-59 -> Par final: 59 -> Decena: 5 -> Color esperado: Rosa
4. Historia: 10-20-80 -> Par final: 80 -> Decena: 8 -> Color esperado: Rojo
Pasos a seguir:
1. Abrir el formulario lateral de nuevo ingreso.
2. Ingresar la historia "12-34-05" en el campo correspondiente. Verificar visualmente el color que muestra el preview interactivo.
3. Repetir ingresando las historias "99-88-23", "00-00-59" y "10-20-80" sucesivamente en el campo de texto, borrando la anterior cada vez.
4. Confirmar que el nombre del color y el preview cambian a los colores esperados.
Resultado esperado:
El sistema asocia en tiempo real y asigna en la interfaz los colores correspondientes:
- Para "05": Marrón (#8B4513)
- Para "23": Verde (#228B22)
- Para "59": Rosa (#FF69B4)
- Para "80": Rojo (#DC143C)
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-027
Caso de prueba:
Visualización de la paleta de colores de referencia (ColoresView)
Descripción del Caso:
Verificar que el módulo de visualización de colores (ColoresView) liste de forma clara e inalterada los 10 colores del sistema, su muestra gráfica y el rango numérico al que corresponden
Precondición:
El usuario debe estar autenticado en el Dashboard.
Datos de prueba:
Ninguno
Pasos a seguir:
1. Hacer clic en el botón "🎨 Colores" del menú lateral del Dashboard.
2. Verificar que se despliega la cuadrícula con las muestras de los colores.
3. Constatar que se muestran los 10 colores definidos (Marrón, Azul Marino, Verde, Naranja, Morado, Rosa, Turquesa, Amarillo, Rojo, Azul Celeste) junto con sus rangos de dígitos de decenas (00-09, 10-19, etc.).
Resultado esperado:
Se visualiza una cuadrícula alineada con cuadrados de color de 60x60px, con su respectivo nombre, rango numérico de decenas asignado y código HEX visible e idéntico a la tabla oficial.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

# GRUPO 6: GESTIÓN DE USUARIOS DEL SISTEMA

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-028
Caso de prueba:
Registro exitoso de nuevo usuario operador
Descripción del Caso:
Verificar que un administrador de sistema pueda registrar un nuevo operador de forma exitosa y que la contraseña sea hasheada con SHA-256 en la base de datos
Precondición:
El usuario administrador debe haber iniciado sesión y estar en la pantalla UsuariosView. El nombre de usuario "op_pedro" y cédula "15000000" no deben estar registrados.
Datos de prueba:
Nombre: Pedro, Apellido: Pérez, Cédula: 15000000, Usuario: op_pedro, Contraseña: clave_segura123
Pasos a seguir:
1. Hacer clic en "👥 Usuarios" en el menú de navegación lateral.
2. Hacer clic en "+ Nuevo Usuario" (o rellenar el formulario lateral de nuevo registro).
3. Ingresar el Nombre: Pedro, Apellido: Pérez, Cédula: 15000000, Usuario: op_pedro, Contraseña: clave_segura123.
4. Presionar el botón "Guardar".
Resultado esperado:
El sistema registra al usuario, limpia el formulario lateral y emite un mensaje de éxito. Pedro Pérez aparece en la lista de usuarios.
En la base de datos SQLite, en la tabla `usuarios`, el campo `clave` no almacena "clave_segura123", sino su hash SHA-256: `9559c63c5a6104bc12ff6b7e8d2e85e0bf5fa346221160875e6d67e7c9f3e46c` (o equivalente).
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-029
Caso de prueba:
Registro fallido - Nombre de usuario ya existente
Descripción del Caso:
Verificar que el sistema rechace el registro de un nuevo operador si su nombre de usuario (nombre de cuenta) ya está registrado en el sistema
Precondición:
El nombre de usuario "op_pedro" debe estar previamente registrado y activo en el sistema.
Datos de prueba:
Nombre: Pedro, Apellido: Rodríguez, Cédula: 16000000, Usuario: op_pedro, Contraseña: otra_clave456
Pasos a seguir:
1. Ir al panel de administración de Usuarios.
2. Intentar registrar un usuario ingresando la misma cuenta de usuario duplicada: "op_pedro".
3. Completar el resto del formulario con datos correctos.
4. Hacer clic en "Guardar".
Resultado esperado:
El sistema impide la transacción y muestra un mensaje de error notificando al operador que el nombre de usuario ya se encuentra registrado y debe elegir otro.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-030
Caso de prueba:
Edición de datos y contraseña de usuario operador
Descripción del Caso:
Verificar que al editar la información de un usuario, sus datos se actualicen en la base de datos y que, si se escribe una nueva contraseña, esta se re-hashee correctamente
Precondición:
El usuario "op_pedro" debe estar registrado en el sistema.
Datos de prueba:
Cambiar Apellido a: Pérez Soto, Nueva Contraseña: pedro_nueva_clave
Pasos a seguir:
1. Buscar y seleccionar al usuario "op_pedro" en la tabla de usuarios.
2. Modificar su Apellido a "Pérez Soto" en el formulario.
3. Escribir "pedro_nueva_clave" en la caja de contraseña.
4. Hacer clic en "Guardar".
Resultado esperado:
El sistema procesa la modificación exitosamente. El usuario Pedro Pérez Soto se muestra en la tabla. Al intentar iniciar sesión con su cuenta, la antigua clave es rechazada y se le permite el acceso únicamente con la clave "pedro_nueva_clave".
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)




---

REPORTE DE CASOS DE PRUEBA
Fecha de Reporte: 09/06/2026
ID:
CP-031
Caso de prueba:
Desactivación lógica de usuario operador
Descripción del Caso:
Verificar que al eliminar a un operador, el sistema desactive su cuenta asignando estado = 0 (Soft Delete), impidiendo que inicie sesión o aparezca en los listados
Precondición:
El usuario "op_pedro" debe estar activo en el sistema.
Datos de prueba:
Usuario a eliminar: op_pedro
Pasos a seguir:
1. Seleccionar al usuario Pedro Pérez Soto en la tabla de la sección Usuarios.
2. Hacer clic en el botón "Eliminar" (o "Desactivar").
3. Confirmar la operación en el mensaje emergente.
4. Intentar iniciar sesión (LoginView) utilizando las credenciales de "op_pedro".
Resultado esperado:
El usuario desaparece de la tabla del panel UsuariosView. En el inicio de sesión, el sistema rechaza sus credenciales de forma permanente arrojando error de autenticación (debido al filtrado por estado activo).
En base de datos SQLite, el registro mantiene su `id` y datos pero el campo `estado` pasa a `0`.
Resultado obtenido:
☐ Aprobado       ☐ Fallido
Observaciones:




Firma de usuario (Probador)
