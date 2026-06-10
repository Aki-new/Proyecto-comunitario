from pydantic import BaseModel, field_validator
from models.num_historia_utils import validar_formato_num_historia


class TarjetaBase(BaseModel):
    num_historia: str
    id_paciente: int
    id_color: int = 0  # Se auto-deriva del num_historia en el controller
    estado: int = 1

    @field_validator("num_historia")
    @classmethod
    def validar_num_historia(cls, v: str) -> str:
        """Valida que el número de historia tenga formato XX-XX-XX."""
        v = v.strip()
        if not validar_formato_num_historia(v):
            raise ValueError(
                "El numero de historia debe tener formato XX-XX-XX "
                "(3 pares de digitos). Ejemplo: 03-77-34"
            )
        return v


class TarjetaCreate(TarjetaBase):
    pass


class Tarjeta(TarjetaBase):
    id: int

    class Config:
        from_attributes = True