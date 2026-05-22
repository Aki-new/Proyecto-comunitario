import sqlite3
from models.tarjeta import TarjetaCreate, Tarjeta
from dao.conexion import ConexionDB


class TarjetaDAO:
    """DAO para operaciones CRUD sobre la tabla 'tarjetas'."""

    def __init__(self):
        self.db = ConexionDB()

    def crear(self, tarjeta: TarjetaCreate) -> int:
        """Inserta una nueva tarjeta. Retorna el id o -1 si num_historia duplicado."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO tarjetas (num_historia, id_paciente, id_color, estado)
            VALUES (?, ?, ?, 1)
        """
        try:
            cursor.execute(query, (
                tarjeta.num_historia,
                tarjeta.id_paciente,
                tarjeta.id_color,
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1
        finally:
            conn.close()

    def obtener_por_paciente(self, id_paciente: int) -> Tarjeta | None:
        """Trae la tarjeta activa de un paciente (relacion 1:1)."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tarjetas WHERE id_paciente = ? AND estado = 1",
            (id_paciente,),
        )
        fila = cursor.fetchone()
        conn.close()
        return Tarjeta(**dict(fila)) if fila else None

    def obtener_por_id(self, id_tarjeta: int) -> Tarjeta | None:
        """Trae una tarjeta activa por su ID."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tarjetas WHERE id = ? AND estado = 1",
            (id_tarjeta,),
        )
        fila = cursor.fetchone()
        conn.close()
        return Tarjeta(**dict(fila)) if fila else None

    def obtener_todos(self) -> list[Tarjeta]:
        """Retorna todas las tarjetas activas."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tarjetas WHERE estado = 1")
        filas = cursor.fetchall()
        conn.close()
        return [Tarjeta(**dict(fila)) for fila in filas]

    def obtener_por_num_historia(self, num_historia: str) -> Tarjeta | None:
        """Busca una tarjeta activa por su numero de historia."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tarjetas WHERE num_historia = ? AND estado = 1",
            (num_historia,),
        )
        fila = cursor.fetchone()
        conn.close()
        return Tarjeta(**dict(fila)) if fila else None

    def paciente_tiene_tarjeta(self, id_paciente: int) -> bool:
        """Verifica si un paciente ya tiene una tarjeta activa (relacion 1:1)."""
        return self.obtener_por_paciente(id_paciente) is not None

    def actualizar(self, id_tarjeta: int, tarjeta: TarjetaCreate) -> bool:
        """Actualiza num_historia e id_color de una tarjeta activa."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE tarjetas
            SET num_historia = ?, id_color = ?
            WHERE id = ? AND estado = 1
        """
        try:
            cursor.execute(query, (
                tarjeta.num_historia,
                tarjeta.id_color,
                id_tarjeta,
            ))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def soft_delete(self, id_tarjeta: int) -> bool:
        """Desactiva una tarjeta (borrado logico)."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE tarjetas SET estado = 0 WHERE id = ? AND estado = 1",
                (id_tarjeta,),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()