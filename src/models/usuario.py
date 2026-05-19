from pydantic import BaseModel

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    cedula: int
    usuario: str
    estado: int = 1  # 1: Activo, 0: Inactivo

class UsuarioCreate(UsuarioBase):
    clave: str  # La contraseña solo se pide al crear/registrar

class Usuario(UsuarioBase):
    id: int

    class Config:
        from_attributes = True