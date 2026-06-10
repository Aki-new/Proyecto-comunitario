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
