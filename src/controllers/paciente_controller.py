from pydantic import ValidationError
from dao.paciente import PacienteDAO
from dao.tarjeta import TarjetaDAO
from dao.color import ColorDAO
from models.paciente import PacienteCreate, Paciente
from models.tarjeta import TarjetaCreate
from models.num_historia_utils import (
    obtener_nombre_color,
    obtener_color_por_num_historia,
    validar_formato_num_historia,
)


class PacienteController:
    """Controlador de pacientes.
    Orquesta la validacion de datos con Pydantic y las operaciones
    CRUD delegando al PacienteDAO y TarjetaDAO.
    """

    def __init__(self):
        self.paciente_dao = PacienteDAO()
        self.tarjeta_dao = TarjetaDAO()
        self.color_dao = ColorDAO()

    def registrar_paciente(self, datos: dict) -> tuple[bool, str, int | None]:
        """Registra un nuevo paciente validando los datos con Pydantic.

        Args:
            datos: Diccionario con los campos del paciente.

        Returns:
            Tupla (exito, mensaje, id_paciente | None).
        """
        try:
            paciente = PacienteCreate(**datos)
        except ValidationError as e:
            errores = self._formatear_errores(e)
            return False, "Errores de validacion:\n" + "\n".join(errores), None

        id_paciente = self.paciente_dao.crear(paciente)

        if id_paciente == -1:
            return False, "Ya existe un paciente con esa cedula.", None

        return True, f"Paciente registrado exitosamente (ID: {id_paciente}).", id_paciente

    def registrar_paciente_con_tarjeta(
        self, datos_paciente: dict, num_historia: str
    ) -> tuple[bool, str]:
        """Registra un paciente y su tarjeta en una sola operacion.
        El color se auto-deriva del numero de historia.

        Args:
            datos_paciente: Diccionario con los campos del paciente.
            num_historia: Numero de historia en formato XX-XX-XX.

        Returns:
            Tupla (exito, mensaje).
        """
        # Validar formato num_historia
        if not validar_formato_num_historia(num_historia):
            return False, (
                "Formato de numero de historia invalido. "
                "Debe ser XX-XX-XX (ej: 03-77-34)."
            )

        # Validar y crear paciente
        try:
            paciente = PacienteCreate(**datos_paciente)
        except ValidationError as e:
            errores = self._formatear_errores(e)
            return False, "Errores en datos del paciente:\n" + "\n".join(errores)

        id_paciente = self.paciente_dao.crear(paciente)
        if id_paciente == -1:
            return False, "Ya existe un paciente con esa cedula."

        # Resolver color automaticamente
        info_color = obtener_color_por_num_historia(num_historia)
        color = self.color_dao.obtener_por_valor(info_color["nombre"])
        if color is None:
            return False, (
                f"Color '{info_color['nombre']}' no encontrado en la base de datos. "
                f"Ejecute el seed para registrar los colores."
            )

        # Crear tarjeta
        try:
            tarjeta = TarjetaCreate(
                num_historia=num_historia,
                id_paciente=id_paciente,
                id_color=color.id,
            )
        except ValidationError as e:
            errores = self._formatear_errores(e)
            return False, "Errores en la tarjeta:\n" + "\n".join(errores)

        id_tarjeta = self.tarjeta_dao.crear(tarjeta)
        if id_tarjeta == -1:
            return False, "Numero de historia duplicado."

        nombre_color = info_color["nombre"]
        return True, (
            f"Paciente (ID: {id_paciente}) y tarjeta (ID: {id_tarjeta}) "
            f"registrados. Color: {nombre_color}."
        )

    def obtener_paciente(self, id_paciente: int) -> tuple[bool, str | Paciente]:
        """Obtiene un paciente por su ID."""
        paciente = self.paciente_dao.obtener_por_id(id_paciente)
        if paciente is None:
            return False, "Paciente no encontrado o inactivo."
        return True, paciente

    def obtener_paciente_por_id(self, id_paciente: int) -> Paciente | None:
        """Obtiene un paciente directamente por su ID."""
        return self.paciente_dao.obtener_por_id(id_paciente)

    def obtener_paciente_por_cedula(self, cedula: str) -> tuple[bool, str | Paciente]:
        """Obtiene un paciente por su cedula."""
        if not cedula or not cedula.strip():
            return False, "Debe ingresar un numero de cedula."
        paciente = self.paciente_dao.obtener_por_cedula(cedula.strip())
        if paciente is None:
            return False, "Paciente no encontrado o inactivo."
        return True, paciente

    def listar_pacientes(self) -> list[Paciente]:
        """Retorna la lista de todos los pacientes activos."""
        return self.paciente_dao.obtener_todos()

    def actualizar_paciente(self, id_paciente: int, datos: dict) -> tuple[bool, str]:
        """Actualiza los datos de un paciente existente."""
        try:
            paciente = PacienteCreate(**datos)
        except ValidationError as e:
            errores = self._formatear_errores(e)
            return False, "Errores de validacion:\n" + "\n".join(errores)

        actualizado = self.paciente_dao.actualizar(id_paciente, paciente)
        if not actualizado:
            return False, "No se pudo actualizar. El paciente no existe, esta inactivo, o la cedula esta duplicada."
        return True, "Paciente actualizado exitosamente."

    def eliminar_paciente(self, id_paciente: int) -> tuple[bool, str]:
        """Realiza un borrado logico del paciente."""
        eliminado = self.paciente_dao.soft_delete(id_paciente)
        if not eliminado:
            return False, "No se pudo desactivar el paciente."
        return True, "Paciente desactivado exitosamente."

    @staticmethod
    def _formatear_errores(e: ValidationError) -> list[str]:
        """Formatea los errores de Pydantic en lista legible."""
        errores = []
        for error in e.errors():
            campo = " -> ".join(str(loc) for loc in error["loc"])
            errores.append(f"  {campo}: {error['msg']}")
        return errores
