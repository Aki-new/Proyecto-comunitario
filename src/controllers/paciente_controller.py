from pydantic import ValidationError
from dao.paciente import PacienteDAO
from dao.tarjeta import TarjetaDAO
from models.paciente import PacienteCreate, Paciente
from models.tarjeta import TarjetaCreate


class PacienteController:
    """Controlador de pacientes.
    Orquesta la validación de datos con Pydantic y las operaciones
    CRUD delegando al PacienteDAO y TarjetaDAO.
    """

    def __init__(self):
        self.paciente_dao = PacienteDAO()
        self.tarjeta_dao = TarjetaDAO()

    def registrar_paciente(self, datos: dict) -> tuple[bool, str]:
        """Registra un nuevo paciente validando los datos con Pydantic.

        Args:
            datos: Diccionario con los campos del paciente:
                - cedula, nombre1, nombre2 (opcional), apellido1,
                  apellido2 (opcional), fecha_nacimiento,
                  lugar_nacimiento, estado_vital

        Returns:
            Tupla (éxito: bool, mensaje: str).
        """
        try:
            paciente = PacienteCreate(**datos)
        except ValidationError as e:
            # Extraer mensajes de error legibles
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                mensaje = error["msg"]
                errores.append(f"• {campo}: {mensaje}")
            return False, "Errores de validación:\n" + "\n".join(errores)

        id_paciente = self.paciente_dao.crear(paciente)

        if id_paciente == -1:
            return False, "Ya existe un paciente con esa cédula."

        return True, f"Paciente registrado exitosamente (ID: {id_paciente})."

    def registrar_paciente_con_tarjeta(
        self, datos_paciente: dict, datos_tarjeta: dict
    ) -> tuple[bool, str]:
        """Registra un paciente y su tarjeta de salud en una sola operación.

        Args:
            datos_paciente: Diccionario con los campos del paciente.
            datos_tarjeta: Diccionario con num_historia e id_color.

        Returns:
            Tupla (éxito: bool, mensaje: str).
        """
        # Paso 1: Validar y crear paciente
        try:
            paciente = PacienteCreate(**datos_paciente)
        except ValidationError as e:
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                mensaje = error["msg"]
                errores.append(f"• {campo}: {mensaje}")
            return False, "Errores en datos del paciente:\n" + "\n".join(errores)

        id_paciente = self.paciente_dao.crear(paciente)

        if id_paciente == -1:
            return False, "Ya existe un paciente con esa cédula."

        # Paso 2: Validar y crear tarjeta asociada al paciente
        datos_tarjeta["id_paciente"] = id_paciente
        try:
            tarjeta = TarjetaCreate(**datos_tarjeta)
        except ValidationError as e:
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                mensaje = error["msg"]
                errores.append(f"• {campo}: {mensaje}")
            return False, "Errores en datos de la tarjeta:\n" + "\n".join(errores)

        id_tarjeta = self.tarjeta_dao.crear(tarjeta)

        if id_tarjeta == -1:
            return False, "Error al crear la tarjeta: número de historia duplicado."

        return True, (
            f"Paciente registrado (ID: {id_paciente}) "
            f"con tarjeta (ID: {id_tarjeta})."
        )

    def obtener_paciente(self, id_paciente: int) -> tuple[bool, str | Paciente]:
        """Obtiene un paciente por su ID.

        Returns:
            Tupla (éxito: bool, Paciente | mensaje_error: str).
        """
        paciente = self.paciente_dao.obtener_por_id(id_paciente)

        if paciente is None:
            return False, "Paciente no encontrado o inactivo."

        return True, paciente

    def obtener_paciente_por_cedula(self, cedula: str) -> tuple[bool, str | Paciente]:
        """Obtiene un paciente por su cédula.

        Returns:
            Tupla (éxito: bool, Paciente | mensaje_error: str).
        """
        if not cedula or not cedula.strip():
            return False, "Debe ingresar un número de cédula."

        paciente = self.paciente_dao.obtener_por_cedula(cedula.strip())

        if paciente is None:
            return False, "Paciente no encontrado o inactivo."

        return True, paciente

    def listar_pacientes(self) -> list[Paciente]:
        """Retorna la lista de todos los pacientes activos."""
        return self.paciente_dao.obtener_todos()

    def actualizar_paciente(
        self, id_paciente: int, datos: dict
    ) -> tuple[bool, str]:
        """Actualiza los datos de un paciente existente.

        Args:
            id_paciente: ID del paciente a actualizar.
            datos: Diccionario con los campos actualizados.

        Returns:
            Tupla (éxito: bool, mensaje: str).
        """
        try:
            paciente = PacienteCreate(**datos)
        except ValidationError as e:
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                mensaje = error["msg"]
                errores.append(f"• {campo}: {mensaje}")
            return False, "Errores de validación:\n" + "\n".join(errores)

        actualizado = self.paciente_dao.actualizar(id_paciente, paciente)

        if not actualizado:
            return False, "No se pudo actualizar. El paciente no existe o está inactivo."

        return True, "Paciente actualizado exitosamente."

    def eliminar_paciente(self, id_paciente: int) -> tuple[bool, str]:
        """Realiza un borrado lógico (soft delete) del paciente.

        Returns:
            Tupla (éxito: bool, mensaje: str).
        """
        eliminado = self.paciente_dao.soft_delete(id_paciente)

        if not eliminado:
            return False, "No se pudo desactivar. El paciente no existe o ya está inactivo."

        return True, "Paciente desactivado exitosamente."
