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
