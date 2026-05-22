import sqlite3
from models.tarjeta import TarjetaCreate, Tarjeta
from dao.conexion import ConexionDB

class TarjetaDAO:
    def __init__(self):
        self.db = ConexionDB()

    def crear(self, tarjeta: TarjetaCreate) -> int:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO tarjetas (num_historia, id_paciente, id_color, estado) VALUES (?, ?, ?, 1)"
        try:
            cursor.execute(query, (tarjeta.num_historia, tarjeta.id_paciente, tarjeta.id_color))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1
        finally:
            conn.close()

    def obtener_por_paciente(self, id_paciente: int) -> Tarjeta | None:
        """R (Read): Trae la tarjeta de un paciente, SIEMPRE Y CUANDO la tarjeta esté activa."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tarjetas WHERE id_paciente = ? AND estado = 1", (id_paciente,))
        fila = cursor.fetchone()
        conn.close()
        return Tarjeta(**dict(fila)) if fila else None

    def actualizar(self, id_tarjeta: int, tarjeta: TarjetaCreate) -> bool:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE tarjetas SET num_historia = ?, id_color = ? WHERE id = ? AND estado = 1"
        try:
            cursor.execute(query, (tarjeta.num_historia, tarjeta.id_color, id_tarjeta))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def soft_delete(self, id_tarjeta: int) -> bool:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE tarjetas SET estado = 0 WHERE id = ?", (id_tarjeta,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()