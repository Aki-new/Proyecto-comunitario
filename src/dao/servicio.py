"""
DAO para la tabla 'servicios' del módulo Tarjetero de Ingresos.

Gestiona operaciones CRUD sobre los servicios hospitalarios
(Obstetricia, Cirugía, Medicina, etc.) y su capacidad de camas.
"""

import sqlite3
from models.servicio import Servicio
from dao.conexion import ConexionDB


class ServicioDAO:
    """Acceso a datos para la tabla de servicios hospitalarios."""

    def __init__(self):
        self.db = ConexionDB()

    def obtener_todos(self) -> list[Servicio]:
        """Retorna todos los servicios activos ordenados por ID."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicios WHERE estado = 1 ORDER BY id")
        filas = cursor.fetchall()
        conn.close()
        return [Servicio(**dict(f)) for f in filas]

    def obtener_por_id(self, id_servicio: int) -> Servicio | None:
        """Retorna un servicio activo por su ID, o None si no existe."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM servicios WHERE id = ? AND estado = 1",
            (id_servicio,),
        )
        fila = cursor.fetchone()
        conn.close()
        return Servicio(**dict(fila)) if fila else None

    def actualizar_camas(self, id_servicio: int, total_camas: int) -> bool:
        """Actualiza el total de camas de un servicio.

        Args:
            id_servicio: ID del servicio a actualizar.
            total_camas: Nueva cantidad de camas.

        Returns:
            True si se actualizó correctamente.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE servicios SET total_camas = ? WHERE id = ? AND estado = 1",
                (total_camas, id_servicio),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
