from pydantic import ValidationError
from dao.usuario import UsuarioDAO
from models.usuario import UsuarioCreate, Usuario


class UsuarioController:
    """Controlador de usuarios.
    Orquesta el CRUD de usuarios con validacion Pydantic.
    """

    def __init__(self):
        self.usuario_dao = UsuarioDAO()

    def registrar_usuario(self, datos: dict) -> tuple[bool, str]:
        """Registra un nuevo usuario.

        Args:
            datos: Diccionario con nombre, apellido, cedula, usuario, clave.

        Returns:
            Tupla (exito, mensaje).
        """
        try:
            usuario = UsuarioCreate(**datos)
        except ValidationError as e:
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                errores.append(f"  {campo}: {error['msg']}")
            return False, "Errores de validacion:\n" + "\n".join(errores)

        id_usuario = self.usuario_dao.crear(usuario)

        if id_usuario == -1:
            return False, "Ya existe un usuario con esa cedula o nombre de usuario."

        return True, f"Usuario registrado exitosamente (ID: {id_usuario})."

    def listar_usuarios(self) -> list[Usuario]:
        """Retorna todos los usuarios activos."""
        return self.usuario_dao.obtener_todos()

    def obtener_usuario(self, id_usuario: int) -> tuple[bool, str | Usuario]:
        """Obtiene un usuario por ID."""
        usuario = self.usuario_dao.obtener_por_id(id_usuario)
        if usuario is None:
            return False, "Usuario no encontrado o inactivo."
        return True, usuario

    def actualizar_usuario(
        self, id_usuario: int, datos: dict
    ) -> tuple[bool, str]:
        """Actualiza un usuario existente.

        Args:
            id_usuario: ID del usuario a actualizar.
            datos: Diccionario con los campos actualizados (incluyendo clave).

        Returns:
            Tupla (exito, mensaje).
        """
        try:
            usuario = UsuarioCreate(**datos)
        except ValidationError as e:
            errores = []
            for error in e.errors():
                campo = " -> ".join(str(loc) for loc in error["loc"])
                errores.append(f"  {campo}: {error['msg']}")
            return False, "Errores de validacion:\n" + "\n".join(errores)

        actualizado = self.usuario_dao.actualizar(id_usuario, usuario)

        if not actualizado:
            return False, "No se pudo actualizar. Cedula o usuario duplicado."

        return True, "Usuario actualizado exitosamente."

    def eliminar_usuario(self, id_usuario: int) -> tuple[bool, str]:
        """Desactiva un usuario (borrado logico)."""
        eliminado = self.usuario_dao.soft_delete(id_usuario)
        if not eliminado:
            return False, "No se pudo desactivar el usuario."
        return True, "Usuario desactivado exitosamente."
