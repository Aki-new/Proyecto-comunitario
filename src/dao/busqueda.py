import sqlite3
from models.busqueda import TarjetaSalida
from dao.conexion import ConexionDB


class BusquedaDAO:
    """DAO para consultas de búsqueda sobre la vista 'vista_paciente_tarjeta'."""

    def __init__(self):
        self.db = ConexionDB()

    def obtener_todos(self) -> list[TarjetaSalida]:
        """Consulta la vista que une pacientes, tarjetas y colores.
        Retorna una lista de objetos TarjetaSalida con la información combinada.
        """
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vista_paciente_tarjeta")
        filas = cursor.fetchall()
        conn.close()
        return [TarjetaSalida(**dict(fila)) for fila in filas]

    def buscar_por_cedula(self, cedula: str) -> list[TarjetaSalida]:
        """Busca pacientes en la vista filtrados por cédula (búsqueda parcial)."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vista_paciente_tarjeta WHERE cedula LIKE ?",
            (f"%{cedula}%",)
        )
        filas = cursor.fetchall()
        conn.close()
        return [TarjetaSalida(**dict(fila)) for fila in filas]

    def buscar_por_nombre(self, nombre: str) -> list[TarjetaSalida]:
        """Busca pacientes en la vista filtrados por primer nombre (búsqueda parcial)."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vista_paciente_tarjeta WHERE nombre1 LIKE ?",
            (f"%{nombre}%",)
        )
        filas = cursor.fetchall()
        conn.close()
        return [TarjetaSalida(**dict(fila)) for fila in filas]

    def buscar_por_apellido(self, apellido: str) -> list[TarjetaSalida]:
        """Busca pacientes en la vista filtrados por primer apellido (búsqueda parcial)."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vista_paciente_tarjeta WHERE apellido1 LIKE ?",
            (f"%{apellido}%",)
        )
        filas = cursor.fetchall()
        conn.close()
        return [TarjetaSalida(**dict(fila)) for fila in filas]

    def buscar_por_num_historia(self, num_historia: str) -> list[TarjetaSalida]:
        """Busca pacientes en la vista filtrados por número de historia."""
        conn = self.db.obtener_conexion()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vista_paciente_tarjeta WHERE num_historia LIKE ?",
            (f"%{num_historia}%",)
        )
        filas = cursor.fetchall()
        conn.close()
        return [TarjetaSalida(**dict(fila)) for fila in filas]
