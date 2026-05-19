from pydantic import BaseModel

class ColorBase(BaseModel):
    valor: str
    estado: int = 1

class Color(ColorBase):
    id: int

    class Config:
        from_attributes = True