"""
DAO para la tabla 'ingresos' del módulo Tarjetero.

Gestiona el registro y egreso de pacientes en servicios hospitalarios.
Los ingresos se eliminan con DELETE (no soft-delete) ya que no se
maneja historial.
"""

import sqlite3
from models.servicio import Ingreso, IngresoCreate, IngresoDetalle
from models.num_historia_utils import MAPA_COLORES
from dao.conexion import ConexionDB


# Mapa nombre_color -> hex para resolución rápida
_COLOR_NOMBRE_A_HEX = {nombre: hex_c for _, (nombre, hex_c) in MAPA_COLORES.items()}


class IngresoDAO:
    """Acceso a datos para la tabla de ingresos hospitalarios."""

    def __init__(self):
        self.db = ConexionDB()

    def crear(self, ingreso: IngresoCreate) -> int:
        """Registra un nuevo ingreso. Retorna el ID o -1 si el paciente ya está ingresado."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO ingresos (id_paciente, id_servicio, fecha_ingreso, estado) "
                "VALUES (?, ?, ?, 1)",
                (ingreso.id_paciente, ingreso.id_servicio,
                 ingreso.fecha_ingreso),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1
        finally:
            conn.close()

    def eliminar(self, id_ingreso: int) -> bool:
        """Elimina un ingreso (egreso / dar de alta). DELETE real, sin historial."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM ingresos WHERE id = ?", (id_ingreso,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def eliminar_por_paciente(self, id_paciente: int) -> bool:
        """Elimina el ingreso activo de un paciente (egreso por paciente)."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM ingresos WHERE id_paciente = ? AND estado = 1",
                (id_paciente,),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def obtener_por_servicio(self, id_servicio: int) -> list[IngresoDetalle]:
        """Retorna los ingresos activos de un servicio con datos enriquecidos.

        Hace JOIN con pacientes, tarjetas y colores para devolver toda la
        información necesaria para la UI del tarjetero.
        """
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, i.id_paciente, i.id_servicio, i.fecha_ingreso,
                   COALESCE(p.cedula, 'S/C') AS cedula,
                   p.nombre1 || COALESCE(' ' || p.nombre2, '') || ' ' ||
                   p.apellido1 || COALESCE(' ' || p.apellido2, '') AS nombre_completo,
                   t.num_historia,
                   c.valor AS color_nombre
            FROM ingresos i
            JOIN pacientes p ON i.id_paciente = p.id
            LEFT JOIN tarjetas t ON t.id_paciente = p.id AND t.estado = 1
            LEFT JOIN colores c ON c.id = t.id_color
            WHERE i.id_servicio = ? AND i.estado = 1
            ORDER BY i.fecha_ingreso
        """, (id_servicio,))
        filas = cursor.fetchall()
        conn.close()
        return [self._fila_a_detalle(dict(f)) for f in filas]

    def contar_por_servicio(self, id_servicio: int) -> int:
        """Cuenta los ingresos activos en un servicio."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM ingresos WHERE id_servicio = ? AND estado = 1",
            (id_servicio,),
        )
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else 0

    def obtener_ingreso_paciente(self, id_paciente: int) -> Ingreso | None:
        """Verifica si un paciente tiene un ingreso activo."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ingresos WHERE id_paciente = ? AND estado = 1",
            (id_paciente,),
        )
        fila = cursor.fetchone()
        conn.close()
        return Ingreso(**dict(fila)) if fila else None

    def obtener_todos(self) -> list[IngresoDetalle]:
        """Retorna todos los ingresos activos con datos enriquecidos."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, i.id_paciente, i.id_servicio, i.fecha_ingreso,
                   COALESCE(p.cedula, 'S/C') AS cedula,
                   p.nombre1 || COALESCE(' ' || p.nombre2, '') || ' ' ||
                   p.apellido1 || COALESCE(' ' || p.apellido2, '') AS nombre_completo,
                   t.num_historia,
                   c.valor AS color_nombre
            FROM ingresos i
            JOIN pacientes p ON i.id_paciente = p.id
            LEFT JOIN tarjetas t ON t.id_paciente = p.id AND t.estado = 1
            LEFT JOIN colores c ON c.id = t.id_color
            WHERE i.estado = 1
            ORDER BY i.id_servicio, i.fecha_ingreso
        """)
        filas = cursor.fetchall()
        conn.close()
        return [self._fila_a_detalle(dict(f)) for f in filas]

    def buscar_pacientes_disponibles(self, termino: str) -> list[dict]:
        """Busca pacientes CON tarjeta que NO estén ingresados.

        Args:
            termino: Texto de búsqueda (se busca en nombre, apellido, cédula).

        Returns:
            Lista de dicts con: id, cedula, nombre_completo, num_historia, color_nombre, color_hex
        """
        return self.buscar_pacientes_por_filtro("todos", termino)

    def buscar_pacientes_por_filtro(self, criterio: str, valor: str) -> list[dict]:
        """Busca pacientes disponibles (con tarjeta, no ingresados) por filtro.

        Reutiliza el patrón de filtros de PacientesView para la búsqueda
        de pacientes en el popup de ingreso del tarjetero.

        Args:
            criterio: Campo de filtro ('todos', 'cedula', 'nombre', 'apellido', 'num_historia').
            valor:    Texto a buscar.

        Returns:
            Lista de dicts con: id, cedula, nombre_completo, num_historia, color_nombre, color_hex
        """
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        patron = f"%{valor}%"

        base_sql = """
            SELECT p.id, COALESCE(p.cedula, 'S/C') AS cedula,
                   p.nombre1 || COALESCE(' ' || p.nombre2, '') || ' ' ||
                   p.apellido1 || COALESCE(' ' || p.apellido2, '') AS nombre_completo,
                   t.num_historia,
                   c.valor AS color_nombre
            FROM pacientes p
            JOIN tarjetas t ON t.id_paciente = p.id AND t.estado = 1
            JOIN colores c ON c.id = t.id_color
            WHERE p.estado = 1
              AND p.id NOT IN (SELECT id_paciente FROM ingresos WHERE estado = 1)
        """

        filtros_sql = {
            "cedula":       ("AND COALESCE(p.cedula, '') LIKE ? COLLATE NOCASE", [patron]),
            "nombre":       ("AND (p.nombre1 LIKE ? COLLATE NOCASE OR COALESCE(p.nombre2, '') LIKE ? COLLATE NOCASE)", [patron, patron]),
            "apellido":     ("AND (p.apellido1 LIKE ? COLLATE NOCASE OR COALESCE(p.apellido2, '') LIKE ? COLLATE NOCASE)", [patron, patron]),
            "num_historia": ("AND t.num_historia LIKE ? COLLATE NOCASE", [patron]),
        }

        if criterio in filtros_sql:
            where, params = filtros_sql[criterio]
            sql = f"{base_sql} {where} ORDER BY p.apellido1, p.nombre1 LIMIT 30"
        else:
            # "todos" — buscar en todos los campos
            sql = f"""{base_sql}
              AND (
                  p.nombre1 LIKE ? COLLATE NOCASE
                  OR COALESCE(p.nombre2, '') LIKE ? COLLATE NOCASE
                  OR p.apellido1 LIKE ? COLLATE NOCASE
                  OR COALESCE(p.apellido2, '') LIKE ? COLLATE NOCASE
                  OR COALESCE(p.cedula, '') LIKE ? COLLATE NOCASE
                  OR t.num_historia LIKE ? COLLATE NOCASE
              )
              ORDER BY p.apellido1, p.nombre1 LIMIT 30"""
            params = [patron] * 6

        cursor.execute(sql, params)
        filas = cursor.fetchall()
        conn.close()
        resultados = []
        for f in filas:
            d = dict(f)
            color_nombre = d.get("color_nombre", "")
            d["color_hex"] = _COLOR_NOMBRE_A_HEX.get(color_nombre, "#888888")
            resultados.append(d)
        return resultados

    def _fila_a_detalle(self, fila: dict) -> IngresoDetalle:
        """Convierte un dict de fila SQL a IngresoDetalle con hex de color."""
        color_nombre = fila.get("color_nombre", "") or ""
        fila["color_hex"] = _COLOR_NOMBRE_A_HEX.get(color_nombre, "#888888")
        if fila.get("num_historia") is None:
            fila["num_historia"] = "S/N"
        if fila.get("color_nombre") is None:
            fila["color_nombre"] = "Sin color"
        return IngresoDetalle(**fila)
