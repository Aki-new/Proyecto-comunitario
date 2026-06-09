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
