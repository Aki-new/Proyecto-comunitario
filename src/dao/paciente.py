import sqlite3
from models.paciente import PacienteCreate, Paciente
from dao.conexion import ConexionDB
from utils.date_utils import formatear_fecha_para_mostrar


class PacienteDAO:
    """DAO para operaciones CRUD sobre la tabla 'pacientes'."""

    def __init__(self):
        self.db = ConexionDB()

    def crear(self, paciente: PacienteCreate) -> int:
        """Inserta un nuevo paciente en la base de datos.
        Retorna el id del paciente creado, o -1 si la cédula ya existe.
        Pacientes con cedula 'S/C' se almacenan con NULL (permite multiples).
        """
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
            INSERT INTO pacientes
                (cedula, nombre1, nombre2, apellido1, apellido2,
                 lugar_nacimiento, fecha_nacimiento, estado_vital, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """
        # S/C -> NULL para que UNIQUE no bloquee multiples sin cedula
        cedula_db = None if paciente.cedula in ("S/C", "", None) else paciente.cedula

        try:
            cursor.execute(query, (
                cedula_db,
                paciente.nombre1,
                paciente.nombre2,
                paciente.apellido1,
                paciente.apellido2,
                paciente.lugar_nacimiento,
                paciente.fecha_nacimiento,
                paciente.estado_vital,
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1
        finally:
            conn.close()

    def _fila_a_paciente(self, fila) -> Paciente:
        """Convierte una fila de BD a Paciente, manejando NULL en cedula."""
        d = dict(fila)
        if d.get("cedula") is None:
            d["cedula"] = "S/C"
        if d.get("fecha_nacimiento"):
            d["fecha_nacimiento"] = formatear_fecha_para_mostrar(d["fecha_nacimiento"])
        return Paciente(**d)

    def obtener_por_id(self, id_paciente: int) -> Paciente | None:
        """Obtiene un paciente activo por su ID desde la tabla 'pacientes'."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM pacientes WHERE id = ? AND estado = 1",
            (id_paciente,)
        )
        fila = cursor.fetchone()
        conn.close()
        return self._fila_a_paciente(fila) if fila else None

    def obtener_por_cedula(self, cedula: str) -> Paciente | None:
        """Obtiene un paciente activo por su número de cédula."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM pacientes WHERE cedula = ? AND estado = 1",
            (cedula,)
        )
        fila = cursor.fetchone()
        conn.close()
        return self._fila_a_paciente(fila) if fila else None

    def obtener_todos(self) -> list[Paciente]:
        """Obtiene todos los pacientes activos."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE estado = 1")
        filas = cursor.fetchall()
        conn.close()
        return [self._fila_a_paciente(fila) for fila in filas]

    def actualizar(self, id_paciente: int, paciente: PacienteCreate) -> bool:
        """Actualiza los datos de un paciente activo en la tabla 'pacientes'.
        Retorna True si se actualizó al menos un registro.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE pacientes
            SET cedula = ?, nombre1 = ?, nombre2 = ?, apellido1 = ?,
                apellido2 = ?, lugar_nacimiento = ?, fecha_nacimiento = ?,
                estado_vital = ?
            WHERE id = ? AND estado = 1
        """
        cedula_db = None if paciente.cedula in ("S/C", "", None) else paciente.cedula

        try:
            cursor.execute(query, (
                cedula_db,
                paciente.nombre1,
                paciente.nombre2,
                paciente.apellido1,
                paciente.apellido2,
                paciente.lugar_nacimiento,
                paciente.fecha_nacimiento,
                paciente.estado_vital,
                id_paciente,
            ))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def soft_delete(self, id_paciente: int) -> bool:
        """Desactiva (borrado lógico) un paciente en la tabla 'pacientes'.
        Retorna True si se desactivó al menos un registro.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE pacientes SET estado = 0 WHERE id = ? AND estado = 1",
                (id_paciente,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()