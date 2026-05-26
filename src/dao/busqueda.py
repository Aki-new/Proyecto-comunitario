import sqlite3
from models.busqueda import TarjetaSalida
from dao.conexion import ConexionDB
from loguru import logger
from time import time


class BusquedaDAO:
    """DAO para consultas de busqueda sobre la vista 'vista_paciente_tarjeta'."""

    def __init__(self):
        self.db = ConexionDB()

    def _ejecutar_consulta(self, query: str, params: tuple = ()) -> list[TarjetaSalida]:
        try:
            """Metodo auxiliar para ejecutar consultas y mapear resultados."""
            tiempo_inicio = time()

            conn = self.db.obtener_conexion()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            filas = cursor.fetchall()

            tiempo_final = time()

            tiempo_consulta = tiempo_inicio - tiempo_final

            logger.success(f"""
                    Consulta exitosa: 
                    Query: {query}
                    params: {params}
                    tiempo: {tiempo_consulta}
                """
                )

            return [TarjetaSalida(**dict(fila)) for fila in filas]
        except:
            logger.error(f"""
                    Se produjo un fallo al ejecutar una consulta: 
                    Query: {query}
                    params: {params}
                """
                )
        finally:
            conn.close()

    def obtener_todos(self) -> list[TarjetaSalida]:
        """Retorna todos los registros de la vista."""
        return self._ejecutar_consulta("SELECT * FROM vista_paciente_tarjeta")

    def buscar_por_cedula(self, cedula: str) -> list[TarjetaSalida]:
        """Busqueda parcial por cedula."""
        return self._ejecutar_consulta(
            "SELECT * FROM vista_paciente_tarjeta WHERE cedula LIKE ?",
            (f"%{cedula}%",),
        )

    def buscar_por_nombre(self, nombre: str) -> list[TarjetaSalida]:
        """Busqueda parcial por nombre completo (nombre1 o nombre2)."""
        return self._ejecutar_consulta(
            "SELECT * FROM vista_paciente_tarjeta WHERE nombre1 LIKE ? OR nombre2 LIKE ?",
            (f"%{nombre}%", f"%{nombre}%"),
        )

    def buscar_por_apellido(self, apellido: str) -> list[TarjetaSalida]:
        """Busqueda parcial por apellido (apellido1 o apellido2)."""
        return self._ejecutar_consulta(
            "SELECT * FROM vista_paciente_tarjeta WHERE apellido1 LIKE ? OR apellido2 LIKE ?",
            (f"%{apellido}%", f"%{apellido}%"),
        )

    def buscar_por_nombre_completo(self, texto: str) -> list[TarjetaSalida]:
        """Busqueda en todos los campos de nombre y apellido."""
        patron = f"%{texto}%"
        return self._ejecutar_consulta(
            "SELECT * FROM vista_paciente_tarjeta "
            "WHERE nombre1 LIKE ? OR nombre2 LIKE ? "
            "OR apellido1 LIKE ? OR apellido2 LIKE ?",
            (patron, patron, patron, patron),
        )

    def buscar_por_fecha_nacimiento(self, fecha: str) -> list[TarjetaSalida]:
        """Busqueda por fecha de nacimiento (parcial o exacta)."""
        return self._ejecutar_consulta(
            "SELECT * FROM vista_paciente_tarjeta WHERE fecha_nacimiento LIKE ?",
            (f"%{fecha}%",),
        )

    def buscar_por_lugar_nacimiento(self, lugar: str) -> list[TarjetaSalida]:
        """Busqueda parcial por lugar de nacimiento."""
        return self._ejecutar_consulta(
            "SELECT * FROM vista_paciente_tarjeta WHERE lugar_nacimiento LIKE ?",
            (f"%{lugar}%",),
        )
