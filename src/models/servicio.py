"""
Modelos Pydantic para el módulo de Tarjetero de Ingresos.

Define las estructuras de datos para servicios hospitalarios e ingresos
de pacientes. Un servicio tiene un número configurable de camas y los
ingresos representan tarjetas de pacientes ocupando camas en un servicio.

Reglas de negocio:
    - Un paciente solo puede estar ingresado en un servicio a la vez.
    - No se maneja historial de ingresos (al egresar se elimina el registro).
    - El egreso es simplemente liberar la cama (dar de alta).
    - No existe entidad "cama" individual, solo se cuenta la cantidad.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional

from utils.date_utils import normalizar_fecha_a_iso


class Servicio(BaseModel):
    """Servicio hospitalario con capacidad de camas.

    Atributos:
        id:          Identificador único del servicio.
        nombre:      Nombre del servicio (ej: 'Obstetricia').
        total_camas: Cantidad total de camas disponibles.
        estado:      1 = activo, 0 = inactivo.
    """
    id: int
    nombre: str
    total_camas: int
    estado: int = 1

    class Config:
        from_attributes = True


class ServicioUpdate(BaseModel):
    """Datos para actualizar la capacidad de camas de un servicio.

    Atributos:
        total_camas: Nueva cantidad total de camas.
    """
    total_camas: int = Field(gt=0)

    @field_validator("total_camas")
    @classmethod
    def validar_camas(cls, v: int) -> int:
        if v < 1:
            raise ValueError("El total de camas debe ser al menos 1.")
        return v


class Ingreso(BaseModel):
    """Registro de un paciente ingresado en un servicio.

    Atributos:
        id:             Identificador único del ingreso.
        id_paciente:    FK al paciente ingresado.
        id_servicio:    FK al servicio donde está ingresado.
        fecha_ingreso:  Fecha de ingreso en formato DD/MM/AAAA.
        estado:         1 = activo, 0 = inactivo.
    """
    id: int
    id_paciente: int
    id_servicio: int
    fecha_ingreso: str
    estado: int = 1

    class Config:
        from_attributes = True


class IngresoCreate(BaseModel):
    """Datos requeridos para registrar un nuevo ingreso.

    Atributos:
        id_paciente:    ID del paciente a ingresar.
        id_servicio:    ID del servicio donde se ingresa.
        fecha_ingreso:  Fecha de ingreso en formato DD-MM-AAAA.
    """
    id_paciente: int
    id_servicio: int
    fecha_ingreso: str

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, v: str) -> str:
        """Valida y normaliza la fecha de ingreso a YYYY-MM-DD."""
        return normalizar_fecha_a_iso(v)


class IngresoDetalle(BaseModel):
    """Ingreso enriquecido con datos del paciente y su tarjeta.

    Se usa para mostrar la información completa en la UI del tarjetero
    sin necesidad de consultas adicionales.

    Atributos:
        id:              ID del ingreso.
        id_paciente:     FK al paciente.
        id_servicio:     FK al servicio.
        fecha_ingreso:   Fecha de ingreso.
        cedula:          Cédula del paciente (o 'S/C').
        nombre_completo: Nombre completo concatenado.
        num_historia:    Número de historia clínica (XX-XX-XX).
        color_nombre:    Nombre del color de la tarjeta.
        color_hex:       Código hex del color para visualización.
    """
    id: int
    id_paciente: int
    id_servicio: int
    fecha_ingreso: str
    cedula: str = "S/C"
    nombre_completo: str = ""
    num_historia: str = ""
    color_nombre: str = ""
    color_hex: str = "#888888"
