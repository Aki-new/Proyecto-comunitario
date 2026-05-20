from pydantic import BaseModel
from typing import Optional

class TarjetaSalida(BaseModel):
    cedula: str
    nombre1: str
    nombre2: Optional[str] = None
    apellido1: str
    apellido2: Optional[str] = None
    fecha_nacimiento: str
    lugar_nacimiento: str
    estado_vital: int
    num_historia: str
    color: str