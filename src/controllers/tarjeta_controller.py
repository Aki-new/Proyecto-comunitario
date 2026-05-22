from pydantic import ValidationError
from dao.tarjeta import TarjetaDAO
from dao.color import ColorDAO
from models.tarjeta import TarjetaCreate, Tarjeta
from models.num_historia_utils import (
    obtener_nombre_color,
    obtener_color_por_num_historia,
    validar_formato_num_historia,
)


class TarjetaController:
    """Controlador de tarjetas de salud.
    Orquesta la validacion, auto-derivacion de color y CRUD.
    """

    def __init__(self):
        self.tarjeta_dao = TarjetaDAO()
        self.color_dao = ColorDAO()

    def _resolver_id_color(self, num_historia: str) -> int | None:
        """Resuelve el id_color a partir del numero de historia.
        Busca el color en la tabla colores por su nombre.
        Retorna el id o None si no se encuentra.
        """
        info_color = obtener_color_por_num_historia(num_historia)
        color = self.color_dao.obtener_por_valor(info_color["nombre"])
        if color is None:
            return None
        return color.id

    def crear_tarjeta(self, id_paciente: int, num_historia: str) -> tuple[bool, str]:
        """Crea una tarjeta para un paciente con auto-derivacion de color.

        Args:
            id_paciente: ID del paciente.
            num_historia: Numero de historia en formato XX-XX-XX.

        Returns:
            Tupla (exito, mensaje).
        """
        # Validar formato
        if not validar_formato_num_historia(num_historia):
            return False, (
                "Formato de numero de historia invalido. "
                "Debe ser XX-XX-XX (ej: 03-77-34)."
            )

        # Verificar que el paciente no tenga ya una tarjeta
        if self.tarjeta_dao.paciente_tiene_tarjeta(id_paciente):
            return False, "El paciente ya tiene una tarjeta activa."

        # Resolver color
        id_color = self._resolver_id_color(num_historia)
        if id_color is None:
            return False, (
                "No se encontro el color correspondiente en la base de datos. "
                "Verifique que los colores esten registrados."
            )

        # Validar y crear
        try:
            tarjeta = TarjetaCreate(
                num_historia=num_historia,
                id_paciente=id_paciente,
                id_color=id_color,
            )
        except ValidationError as e:
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                errores.append(f"  {campo}: {error['msg']}")
            return False, "Errores de validacion:\n" + "\n".join(errores)

        id_tarjeta = self.tarjeta_dao.crear(tarjeta)

        if id_tarjeta == -1:
            return False, "Ya existe una tarjeta con ese numero de historia."

        nombre_color = obtener_nombre_color(num_historia)
        return True, (
            f"Tarjeta creada (ID: {id_tarjeta}). "
            f"Color asignado: {nombre_color}."
        )

    def actualizar_tarjeta(
        self, id_tarjeta: int, num_historia: str
    ) -> tuple[bool, str]:
        """Actualiza el numero de historia (y recalcula el color).

        Args:
            id_tarjeta: ID de la tarjeta a actualizar.
            num_historia: Nuevo numero de historia.

        Returns:
            Tupla (exito, mensaje).
        """
        if not validar_formato_num_historia(num_historia):
            return False, (
                "Formato invalido. Debe ser XX-XX-XX (ej: 03-77-34)."
            )

        tarjeta_actual = self.tarjeta_dao.obtener_por_id(id_tarjeta)
        if tarjeta_actual is None:
            return False, "Tarjeta no encontrada o inactiva."

        id_color = self._resolver_id_color(num_historia)
        if id_color is None:
            return False, "No se encontro el color correspondiente."

        try:
            tarjeta = TarjetaCreate(
                num_historia=num_historia,
                id_paciente=tarjeta_actual.id_paciente,
                id_color=id_color,
            )
        except ValidationError as e:
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                errores.append(f"  {campo}: {error['msg']}")
            return False, "Errores de validacion:\n" + "\n".join(errores)

        actualizado = self.tarjeta_dao.actualizar(id_tarjeta, tarjeta)

        if not actualizado:
            return False, "No se pudo actualizar. Numero de historia duplicado."

        nombre_color = obtener_nombre_color(num_historia)
        return True, (
            f"Tarjeta actualizada. Nuevo color: {nombre_color}."
        )

    def obtener_tarjeta_paciente(self, id_paciente: int) -> Tarjeta | None:
        """Obtiene la tarjeta activa de un paciente."""
        return self.tarjeta_dao.obtener_por_paciente(id_paciente)

    def listar_tarjetas(self) -> list[Tarjeta]:
        """Lista todas las tarjetas activas."""
        return self.tarjeta_dao.obtener_todos()

    def eliminar_tarjeta(self, id_tarjeta: int) -> tuple[bool, str]:
        """Desactiva una tarjeta (borrado logico)."""
        eliminado = self.tarjeta_dao.soft_delete(id_tarjeta)
        if not eliminado:
            return False, "No se pudo desactivar la tarjeta."
        return True, "Tarjeta desactivada exitosamente."
