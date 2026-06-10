"""
Controlador de búsqueda — SGI Salud.

Orquesta las consultas sobre la vista combinada paciente-tarjeta-color.
Soporta búsqueda por: todos, cédula, nombre_completo (multi-palabra),
apellido, fecha_nacimiento, lugar_nacimiento y num_historia.

Cambios v3:
    - Añadido criterio 'num_historia' para buscar por N. de Historia.
    - Búsqueda por nombre_completo ahora es multi-palabra inteligente.
"""

from dao.busqueda import BusquedaDAO
from models.busqueda import TarjetaSalida


class BusquedaController:
    """Controlador de búsqueda.

    Orquesta las consultas sobre la vista paciente-tarjeta-color.

    Métodos:
        buscar(criterio, valor) → (bool, list[TarjetaSalida] | str)
        obtener_todos()         → list[TarjetaSalida]
    """

    def __init__(self):
        self.busqueda_dao = BusquedaDAO()

    def buscar(self, criterio: str, valor: str) -> tuple[bool, str | list[TarjetaSalida]]:
        """Busca registros según el criterio seleccionado.

        Args:
            criterio: Tipo de búsqueda. Valores válidos:
                'todos', 'cedula', 'nombre_completo', 'apellido',
                'fecha_nacimiento', 'lugar_nacimiento', 'num_historia'.
            valor: Texto a buscar.

        Returns:
            Tupla (éxito, resultados | mensaje_error).
        """
        if criterio != "todos" and (not valor or not valor.strip()):
            return False, "Debe ingresar un valor de búsqueda."

        valor = valor.strip() if valor else ""

        try:
            metodos = {
                "todos": self.busqueda_dao.obtener_todos,
                "cedula": lambda: self.busqueda_dao.buscar_por_cedula(valor),
                "nombre_completo": lambda: self.busqueda_dao.buscar_por_nombre_completo(valor),
                "apellido": lambda: self.busqueda_dao.buscar_por_apellido(valor),
                "fecha_nacimiento": lambda: self.busqueda_dao.buscar_por_fecha_nacimiento(valor),
                "lugar_nacimiento": lambda: self.busqueda_dao.buscar_por_lugar_nacimiento(valor),
                "num_historia": lambda: self.busqueda_dao.buscar_por_num_historia(valor),
            }

            fn = metodos.get(criterio)
            if fn is None:
                return False, f"Criterio de búsqueda no válido: '{criterio}'."

            resultados = fn()
            return True, resultados

        except Exception as e:
            return False, f"Error al realizar la búsqueda: {str(e)}"

    def obtener_todos(self, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Retorna todos los registros de la vista paginados."""
        return self.busqueda_dao.obtener_todos(limit, offset)

    def buscar_multicriterio(self, filtros: dict, limit: int = None, offset: int = None) -> tuple[bool, str | tuple[list[TarjetaSalida], int]]:
        """Busca registros combinando múltiples criterios (AND).

        Args:
            filtros: Dict con filtros a aplicar.

        Returns:
            Tupla (éxito, resultados | mensaje_error).
        """
        try:
            resultados = self.busqueda_dao.buscar_multicriterio(filtros, limit, offset)
            return True, resultados
        except Exception as e:
            return False, f"Error al realizar la búsqueda multi-criterio: {str(e)}"
