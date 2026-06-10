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
