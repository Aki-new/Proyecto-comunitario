import sqlite3
from models.color import ColorBase, Color
from dao.conexion import ConexionDB

class ColorDAO:
    def __init__(self):
        self.db = ConexionDB()

    def crear(self, color: ColorBase) -> int:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO colores (valor, estado) VALUES (?, 1)", (color.valor,))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1
        finally:
            conn.close()

    def obtener_activos(self) -> list[Color]:
        """R (Read): Filtra colores activos."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM colores WHERE estado = 1")
        filas = cursor.fetchall()
        conn.close()
        return [Color(**dict(fila)) for fila in filas]

    def actualizar(self, id_color: int, color: ColorBase) -> bool:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE colores SET valor = ? WHERE id = ? AND estado = 1", (color.valor, id_color))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def soft_delete(self, id_color: int) -> bool:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE colores SET estado = 0 WHERE id = ?", (id_color,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()