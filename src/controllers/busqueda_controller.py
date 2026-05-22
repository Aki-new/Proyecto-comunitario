from dao.busqueda import BusquedaDAO
from models.busqueda import TarjetaSalida


class BusquedaController:
    """Controlador de busqueda.
    Orquesta las consultas sobre la vista paciente-tarjeta-color.
    """

    def __init__(self):
        self.busqueda_dao = BusquedaDAO()

    def buscar(self, criterio: str, valor: str) -> tuple[bool, str | list[TarjetaSalida]]:
        """Busca registros segun el criterio seleccionado.

        Args:
            criterio: Tipo de busqueda ('todos', 'cedula', 'nombre_completo',
                      'apellido', 'fecha_nacimiento', 'lugar_nacimiento').
            valor: Texto a buscar.

        Returns:
            Tupla (exito, resultados | mensaje_error).
        """
        if criterio != "todos" and (not valor or not valor.strip()):
            return False, "Debe ingresar un valor de busqueda."

        valor = valor.strip() if valor else ""

        try:
            metodos = {
                "todos": self.busqueda_dao.obtener_todos,
                "cedula": lambda: self.busqueda_dao.buscar_por_cedula(valor),
                "nombre_completo": lambda: self.busqueda_dao.buscar_por_nombre_completo(valor),
                "apellido": lambda: self.busqueda_dao.buscar_por_apellido(valor),
                "fecha_nacimiento": lambda: self.busqueda_dao.buscar_por_fecha_nacimiento(valor),
                "lugar_nacimiento": lambda: self.busqueda_dao.buscar_por_lugar_nacimiento(valor),
            }

            fn = metodos.get(criterio)
            if fn is None:
                return False, f"Criterio de busqueda no valido: '{criterio}'."

            resultados = fn()
            return True, resultados

        except Exception as e:
            return False, f"Error al realizar la busqueda: {str(e)}"

    def obtener_todos(self) -> list[TarjetaSalida]:
        """Retorna todos los registros de la vista."""
        return self.busqueda_dao.obtener_todos()
