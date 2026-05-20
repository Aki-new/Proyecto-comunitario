from pydantic import BaseModel, Field
from typing import Optional

class PacienteBase(BaseModel):
    cedula: str = Field(..., min_length=1, max_length=15)
    nombre1: str
    nombre2: Optional[str] = None
    apellido1: str
    apellido2: Optional[str] = None
    fecha_nacimiento: str  # Formato YYYY-MM-DD
    lugar_nacimiento: str
    estado_vital: int = 1  # 1: Vivo, 0: Fallecido (según tu SQL)
    estado: int = 1

class PacienteCreate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id: int

    class Config:
        from_attributes = True