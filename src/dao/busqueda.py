"""
DAO de búsqueda sobre la vista combinada paciente-tarjeta-color.

Ejecuta consultas sobre `vista_paciente_tarjeta` para la búsqueda
de pacientes con sus tarjetas y colores asociados.

Cambios v3:
    - Búsqueda por nombre_completo mejorada: soporta múltiples palabras
      buscando cada palabra en TODOS los campos de nombre y apellido.
    - Todas las búsquedas son case-insensitive gracias a COLLATE NOCASE.
    - Añadida búsqueda por num_historia.
    - Resultados ordenados por apellido1, nombre1 por defecto.
"""

import sqlite3
from models.busqueda import TarjetaSalida
from dao.conexion import ConexionDB


class BusquedaDAO:
    """DAO para consultas sobre la vista 'vista_paciente_tarjeta'.

    Todos los métodos de búsqueda usan coincidencia parcial (LIKE)
    y retornan listas de TarjetaSalida ordenadas por apellido+nombre.
    """

    _ORDEN = " ORDER BY apellido1, nombre1"

    def __init__(self):
        self.db = ConexionDB()

    def _ejecutar_consulta(self, query: str, params: tuple = ()) -> list[TarjetaSalida]:
        """Ejecuta una consulta SQL y mapea las filas a TarjetaSalida.

        Args:
            query:  Consulta SQL sobre vista_paciente_tarjeta.
            params: Parámetros para la consulta (para evitar SQL injection).

        Returns:
            Lista de TarjetaSalida con los resultados.
        """
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        filas = cursor.fetchall()
        conn.close()
        return [TarjetaSalida(**dict(fila)) for fila in filas]

    # ══════════════════════════════════════════════════════════════════
    #  CONSULTAS
    # ══════════════════════════════════════════════════════════════════

    def obtener_todos(self) -> list[TarjetaSalida]:
        """Retorna todos los registros de la vista, ordenados."""
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta{self._ORDEN}"
        )

    def buscar_por_cedula(self, cedula: str) -> list[TarjetaSalida]:
        """Búsqueda parcial por cédula (case-insensitive)."""
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta "
            f"WHERE cedula LIKE ? COLLATE NOCASE{self._ORDEN}",
            (f"%{cedula}%",),
        )

    def buscar_por_nombre(self, nombre: str) -> list[TarjetaSalida]:
        """Búsqueda parcial por nombre completo (nombre1 y nombre2 concatenados)."""
        v = nombre.strip()
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta "
            f"WHERE (nombre1 || ' ' || COALESCE(nombre2, '')) LIKE ? COLLATE NOCASE{self._ORDEN}",
            (f"%{v}%",),
        )

    def buscar_por_apellido(self, apellido: str) -> list[TarjetaSalida]:
        """Búsqueda parcial por apellido completo (apellido1 y apellido2 concatenados)."""
        v = apellido.strip()
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta "
            f"WHERE (apellido1 || ' ' || COALESCE(apellido2, '')) LIKE ? COLLATE NOCASE{self._ORDEN}",
            (f"%{v}%",),
        )

    def buscar_por_nombre_completo(self, texto: str) -> list[TarjetaSalida]:
        """Búsqueda inteligente por nombre completo (multi-palabra).

        Cada palabra del texto se busca en TODOS los campos de nombre
        y apellido. Un registro coincide solo si TODAS las palabras
        aparecen en al menos un campo.

        Ejemplo:
            texto = "Maria Gonzalez"
            → Busca registros donde "Maria" esté en nombre1/nombre2/apellido1/apellido2
              Y "Gonzalez" esté en nombre1/nombre2/apellido1/apellido2.

        Args:
            texto: Texto de búsqueda (puede tener varias palabras).

        Returns:
            Lista de TarjetaSalida que coinciden con todas las palabras.
        """
        palabras = texto.strip().split()
        if not palabras:
            return self.obtener_todos()

        # Construir condición AND para cada palabra
        condiciones = []
        parametros = []
        for palabra in palabras:
            cond = (
                "(nombre1 LIKE ? COLLATE NOCASE "
                "OR COALESCE(nombre2,'') LIKE ? COLLATE NOCASE "
                "OR apellido1 LIKE ? COLLATE NOCASE "
                "OR COALESCE(apellido2,'') LIKE ? COLLATE NOCASE)"
            )
            condiciones.append(cond)
            patron = f"%{palabra}%"
            parametros.extend([patron, patron, patron, patron])

        where = " AND ".join(condiciones)
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta WHERE {where}{self._ORDEN}",
            tuple(parametros),
        )

    def buscar_por_fecha_nacimiento(self, fecha: str) -> list[TarjetaSalida]:
        """Búsqueda por fecha de nacimiento (parcial o exacta)."""
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta "
            f"WHERE fecha_nacimiento LIKE ?{self._ORDEN}",
            (f"%{fecha}%",),
        )

    def buscar_por_lugar_nacimiento(self, lugar: str) -> list[TarjetaSalida]:
        """Búsqueda parcial por lugar de nacimiento (case-insensitive)."""
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta "
            f"WHERE lugar_nacimiento LIKE ? COLLATE NOCASE{self._ORDEN}",
            (f"%{lugar}%",),
        )

    def buscar_por_num_historia(self, num_historia: str) -> list[TarjetaSalida]:
        """Búsqueda parcial por número de historia."""
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta "
            f"WHERE num_historia LIKE ?{self._ORDEN}",
            (f"%{num_historia}%",),
        )

    def buscar_multicriterio(self, filtros: dict) -> list[TarjetaSalida]:
        """Búsqueda avanzada multi-criterio combinando filtros con AND.

        Args:
            filtros: Dict con claves de búsqueda y sus valores.
                     Claves soportadas:
                     - 'cedula': str
                     - 'nombre': str
                     - 'apellido': str
                     - 'lugar_nacimiento': str
                     - 'fecha_nacimiento': str (YYYY-MM-DD o parcial)
                     - 'fecha_nacimiento_partes': tuple[str, str, str] (dia, mes, anio)

        Returns:
            Lista de TarjetaSalida que cumplen con todos los filtros.
        """
        if not filtros:
            return self.obtener_todos()

        condiciones = []
        parametros = []

        for clave, valor in filtros.items():
            if valor is None:
                continue

            if clave == "cedula":
                v = str(valor).strip()
                if v:
                    condiciones.append("cedula LIKE ? COLLATE NOCASE")
                    parametros.append(f"%{v}%")

            elif clave == "nombre":
                v = str(valor).strip()
                if v:
                    condiciones.append("(nombre1 || ' ' || COALESCE(nombre2,'')) LIKE ? COLLATE NOCASE")
                    parametros.append(f"%{v}%")

            elif clave == "apellido":
                v = str(valor).strip()
                if v:
                    condiciones.append("(apellido1 || ' ' || COALESCE(apellido2,'')) LIKE ? COLLATE NOCASE")
                    parametros.append(f"%{v}%")

            elif clave == "lugar_nacimiento":
                v = str(valor).strip()
                if v:
                    condiciones.append("lugar_nacimiento LIKE ? COLLATE NOCASE")
                    parametros.append(f"%{v}%")

            elif clave == "fecha_nacimiento":
                v = str(valor).strip()
                if v:
                    condiciones.append("fecha_nacimiento LIKE ?")
                    parametros.append(f"%{v}%")

            elif clave == "fecha_nacimiento_partes":
                # valor es (dia, mes, anio)
                dia, mes, anio = valor
                if dia and str(dia).strip():
                    try:
                        dia_val = f"{int(dia):02d}"
                        condiciones.append("strftime('%d', fecha_nacimiento) = ?")
                        parametros.append(dia_val)
                    except ValueError:
                        pass
                if mes and str(mes).strip():
                    try:
                        mes_val = f"{int(mes):02d}"
                        condiciones.append("strftime('%m', fecha_nacimiento) = ?")
                        parametros.append(mes_val)
                    except ValueError:
                        pass
                if anio and str(anio).strip():
                    try:
                        anio_val = f"{int(anio):04d}"
                        condiciones.append("strftime('%Y', fecha_nacimiento) = ?")
                        parametros.append(anio_val)
                    except ValueError:
                        pass

        if not condiciones:
            return self.obtener_todos()

        where = " AND ".join(condiciones)
        return self._ejecutar_consulta(
            f"SELECT * FROM vista_paciente_tarjeta WHERE {where}{self._ORDEN}",
            tuple(parametros),
        )
