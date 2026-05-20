import sqlite3
from models.paciente import PacienteCreate, Paciente
from dao.conexion import ConexionDB

class PacienteDAO:
    def __init__(self):
        self.db = ConexionDB()

    def crear(self, paciente: PacienteCreate) -> int:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO pacientes (cedula, nombre1, nombre2, apellido1, apellido2, lugar_nacimiento, fecha_nacimiento, estado_vital, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)"
        try:
            cursor.execute(query, (paciente.cedula, paciente.nombre1, paciente.nombre2, paciente.apellido1, paciente.apellido2, paciente.lugar_nacimiento, paciente.fecha_nacimiento, paciente.estado_vital, paciente.estado))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1
        finally:
            conn.close()

    def obtener_por_id(self, id_paciente: int) -> Paciente | None:
        """R (Read): Trae la tarjeta de un paciente, SIEMPRE Y CUANDO la tarjeta esté activa."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tarjetas WHERE id_paciente = ? AND estado = 1", (id_paciente,))
        fila = cursor.fetchone()
        conn.close()
        return Paciente(**dict(fila)) if fila else None

    def actualizar(self, id_tarjeta: int, tarjeta: PacienteCreate) -> bool:
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