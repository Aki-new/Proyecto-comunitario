"""
Controlador del módulo Tarjetero de Ingresos.

Gestiona la lógica de negocio para registrar y dar de alta pacientes
en servicios hospitalarios. Coordina las validaciones entre servicios,
pacientes, tarjetas e ingresos.
"""

from loguru import logger
from dao.servicio import ServicioDAO
from dao.ingreso import IngresoDAO
from dao.tarjeta import TarjetaDAO
from dao.paciente import PacienteDAO
from models.servicio import IngresoCreate


class IngresoController:
    """Controlador para el tarjetero de ingresos hospitalarios.

    Coordina la gestión de ingresos y egresos de pacientes en servicios,
    validando reglas de negocio como disponibilidad de camas, existencia
    de tarjeta, y unicidad de ingreso por paciente.
    """

    def __init__(self):
        self.servicio_dao = ServicioDAO()
        self.ingreso_dao = IngresoDAO()
        self.tarjeta_dao = TarjetaDAO()
        self.paciente_dao = PacienteDAO()

    def listar_servicios(self):
        """Retorna la lista de servicios hospitalarios activos."""
        return self.servicio_dao.obtener_todos()

    def obtener_resumen_servicio(self, id_servicio: int) -> dict:
        """Obtiene el resumen completo de un servicio.

        Returns:
            Dict con: servicio, total_camas, ocupadas, disponibles, ingresos.
        """
        servicio = self.servicio_dao.obtener_por_id(id_servicio)
        if not servicio:
            return None
        ingresos = self.ingreso_dao.obtener_por_servicio(id_servicio)
        ocupadas = len(ingresos)
        return {
            "servicio": servicio,
            "total_camas": servicio.total_camas,
            "ocupadas": ocupadas,
            "disponibles": servicio.total_camas - ocupadas,
            "ingresos": ingresos,
        }

    def obtener_resumen_general(self) -> list[dict]:
        """Obtiene el resumen de todos los servicios con conteo de ocupación."""
        servicios = self.servicio_dao.obtener_todos()
        resumen = []
        for s in servicios:
            ocupadas = self.ingreso_dao.contar_por_servicio(s.id)
            resumen.append({
                "servicio": s,
                "total_camas": s.total_camas,
                "ocupadas": ocupadas,
                "disponibles": s.total_camas - ocupadas,
            })
        return resumen

    def registrar_ingreso(self, datos: dict) -> tuple[bool, str]:
        """Registra el ingreso de un paciente a un servicio.

        Validaciones:
            - El paciente debe existir y estar activo.
            - El paciente debe tener una tarjeta activa.
            - El paciente no debe estar ya ingresado en ningún servicio.
            - El servicio debe tener camas disponibles.

        Args:
            datos: Dict con id_paciente, id_servicio, fecha_ingreso.

        Returns:
            Tupla (éxito: bool, mensaje: str).
        """
        try:
            id_paciente = datos.get("id_paciente")
            id_servicio = datos.get("id_servicio")
            fecha = datos.get("fecha_ingreso", "").strip()

            if not id_paciente or not id_servicio:
                return False, "Debe seleccionar un paciente y un servicio."
            if not fecha:
                return False, "La fecha de ingreso es obligatoria."

            # Verificar paciente
            paciente = self.paciente_dao.obtener_por_id(id_paciente)
            if not paciente:
                return False, "El paciente no existe o está inactivo."

            # Verificar tarjeta
            tarjeta = self.tarjeta_dao.obtener_por_paciente(id_paciente)
            if not tarjeta:
                return False, "El paciente no tiene una tarjeta asignada."

            # Verificar que no esté ya ingresado
            ingreso_existente = self.ingreso_dao.obtener_ingreso_paciente(id_paciente)
            if ingreso_existente:
                servicio_actual = self.servicio_dao.obtener_por_id(ingreso_existente.id_servicio)
                nombre_servicio = servicio_actual.nombre if servicio_actual else "otro servicio"
                return False, f"El paciente ya está ingresado en {nombre_servicio}."

            # Verificar disponibilidad de camas
            servicio = self.servicio_dao.obtener_por_id(id_servicio)
            if not servicio:
                return False, "El servicio no existe."
            ocupadas = self.ingreso_dao.contar_por_servicio(id_servicio)
            if ocupadas >= servicio.total_camas:
                return False, f"No hay camas disponibles en {servicio.nombre} ({ocupadas}/{servicio.total_camas})."

            # Crear ingreso
            ingreso = IngresoCreate(
                id_paciente=id_paciente,
                id_servicio=id_servicio,
                fecha_ingreso=fecha,
            )
            resultado = self.ingreso_dao.crear(ingreso)
            if resultado == -1:
                return False, "Error: el paciente ya tiene un ingreso registrado."

            logger.info(f"Ingreso registrado: paciente {id_paciente} en servicio {servicio.nombre}")
            return True, f"Paciente ingresado exitosamente en {servicio.nombre}."

        except Exception as e:
            logger.error(f"Error al registrar ingreso: {e}")
            return False, f"Error inesperado: {e}"

    def registrar_egreso(self, id_ingreso: int) -> tuple[bool, str]:
        """Da de alta a un paciente (elimina el ingreso, liberando la cama).

        Args:
            id_ingreso: ID del registro de ingreso a eliminar.

        Returns:
            Tupla (éxito: bool, mensaje: str).
        """
        try:
            resultado = self.ingreso_dao.eliminar(id_ingreso)
            if resultado:
                logger.info(f"Egreso registrado: ingreso {id_ingreso} eliminado")
                return True, "Paciente dado de alta exitosamente."
            return False, "No se encontró el ingreso especificado."
        except Exception as e:
            logger.error(f"Error al registrar egreso: {e}")
            return False, f"Error inesperado: {e}"

    def actualizar_camas_servicio(self, id_servicio: int, total_camas: int) -> tuple[bool, str]:
        """Actualiza la cantidad de camas de un servicio.

        Validación: No se puede reducir por debajo de las camas actualmente ocupadas.

        Args:
            id_servicio: ID del servicio.
            total_camas: Nueva cantidad de camas.

        Returns:
            Tupla (éxito: bool, mensaje: str).
        """
        try:
            if total_camas < 1:
                return False, "El total de camas debe ser al menos 1."

            ocupadas = self.ingreso_dao.contar_por_servicio(id_servicio)
            if total_camas < ocupadas:
                return False, (
                    f"No se puede reducir a {total_camas} camas. "
                    f"Actualmente hay {ocupadas} camas ocupadas."
                )

            resultado = self.servicio_dao.actualizar_camas(id_servicio, total_camas)
            if resultado:
                logger.info(f"Camas actualizadas: servicio {id_servicio} → {total_camas}")
                return True, f"Capacidad actualizada a {total_camas} camas."
            return False, "No se encontró el servicio."
        except Exception as e:
            logger.error(f"Error al actualizar camas: {e}")
            return False, f"Error inesperado: {e}"

    def buscar_pacientes_disponibles(self, termino: str) -> list[dict]:
        """Busca pacientes con tarjeta que no estén ingresados.

        Args:
            termino: Texto de búsqueda.

        Returns:
            Lista de dicts con datos del paciente y su tarjeta.
        """
        return self.ingreso_dao.buscar_pacientes_disponibles(termino)

    def buscar_pacientes_por_filtro(self, criterio: str, valor: str) -> list[dict]:
        """Busca pacientes disponibles filtrando por un criterio específico.

        Reutiliza el mismo patrón de filtros que la vista de Pacientes.

        Args:
            criterio: 'todos', 'cedula', 'nombre', 'apellido', 'num_historia'.
            valor:    Texto a buscar.

        Returns:
            Lista de dicts con datos del paciente y su tarjeta.
        """
        return self.ingreso_dao.buscar_pacientes_por_filtro(criterio, valor)
