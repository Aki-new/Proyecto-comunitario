"""Modelo Pydantic de Paciente con validaciones de formato."""

import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ── Patrones de validacion ────────────────────────────────────────
# Cedula: V-12345678 o E-12345678 (letra + guion + 6-10 digitos)
# Tambien acepta vacio/S-C para ninos sin cedula
PATRON_CEDULA = re.compile(r"^[VvEe]-\d{6,10}$")

# Fecha: DD/MM/YYYY o DD-MM-YYYY
PATRON_FECHA = re.compile(r"^\d{2}[/\-]\d{2}[/\-]\d{4}$")


class PacienteBase(BaseModel):
    cedula: str = Field(default="S/C", max_length=15)
    nombre1: str
    nombre2: Optional[str] = None
    apellido1: str
    apellido2: Optional[str] = None
    fecha_nacimiento: str
    lugar_nacimiento: str
    estado_vital: int = 1  # 1: Vivo, 0: Fallecido
    estado: int = 1

    @field_validator("cedula")
    @classmethod
    def validar_cedula(cls, v: str) -> str:
        """Valida el formato de la cedula.
        Acepta: V-12345678, E-12345678, S/C (sin cedula para ninos).
        """
        v = v.strip()
        if not v or v.upper() == "S/C":
            return "S/C"

        # Normalizar: primera letra a mayuscula
        v = v[0].upper() + v[1:]

        if not PATRON_CEDULA.match(v):
            raise ValueError(
                "Formato de cedula invalido. "
                "Use V-12345678 o E-12345678 (6 a 10 digitos)."
            )
        return v

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha(cls, v: str) -> str:
        """Valida y normaliza la fecha de nacimiento.
        Acepta DD/MM/YYYY o DD-MM-YYYY. Normaliza a DD/MM/YYYY.
        """
        v = v.strip()
        if not PATRON_FECHA.match(v):
            raise ValueError(
                "Formato de fecha invalido. "
                "Use DD/MM/YYYY o DD-MM-YYYY (ej: 21/02/2026)."
            )

        # Normalizar separadores a /
        v = v.replace("-", "/")

        # Validar que la fecha sea logica
        partes = v.split("/")
        dia, mes, anio = int(partes[0]), int(partes[1]), int(partes[2])

        if mes < 1 or mes > 12:
            raise ValueError("Mes invalido (debe ser 01-12).")
        if dia < 1 or dia > 31:
            raise ValueError("Dia invalido (debe ser 01-31).")
        if anio < 1900 or anio > 2100:
            raise ValueError("Anio invalido (debe ser 1900-2100).")

        return v

    @field_validator("nombre1", "apellido1")
    @classmethod
    def validar_no_vacio(cls, v: str) -> str:
        """Valida que los campos obligatorios no esten vacios."""
        v = v.strip()
        if not v:
            raise ValueError("Este campo es obligatorio.")
        return v

    @field_validator("lugar_nacimiento")
    @classmethod
    def validar_lugar(cls, v: str) -> str:
        """Valida que el lugar de nacimiento no este vacio."""
        v = v.strip()
        if not v:
            raise ValueError("El lugar de nacimiento es obligatorio.")
        return v


class PacienteCreate(PacienteBase):
    pass


class Paciente(PacienteBase):
    id: int

    class Config:
        from_attributes = True