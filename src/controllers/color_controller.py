from dao.color import ColorDAO
from models.color import Color
from models.num_historia_utils import LISTA_COLORES


class ColorController:
    """Controlador de colores.
    Los colores son fijos (determinados por el rango del numero de historia).
    Este controlador es principalmente de consulta.
    """

    def __init__(self):
        self.color_dao = ColorDAO()

    def listar_colores(self) -> list[Color]:
        """Retorna todos los colores activos de la base de datos."""
        return self.color_dao.obtener_todos()

    def obtener_referencia_colores(self) -> list[dict]:
        """Retorna la tabla de referencia completa de colores y rangos.
        No depende de la base de datos, usa la constante LISTA_COLORES.
        """
        return LISTA_COLORES

    def obtener_color(self, id_color: int) -> Color | None:
        """Obtiene un color por su ID."""
        return self.color_dao.obtener_por_id(id_color)
