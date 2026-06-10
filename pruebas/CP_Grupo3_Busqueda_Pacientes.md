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
