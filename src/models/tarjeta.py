from pydantic import BaseModel

class TarjetaBase(BaseModel):
    num_historia: str
    id_paciente: int
    id_color: int
    estado: int = 1

class TarjetaCreate(TarjetaBase):
    pass

class Tarjeta(TarjetaBase):
    id: int

    class Config:
        from_attributes = True