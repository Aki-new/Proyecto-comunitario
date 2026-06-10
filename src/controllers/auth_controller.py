from dao.usuario import UsuarioDAO
from models.usuario import Usuario


class AuthController:
    """Controlador de autenticación.
    Conecta la Vista de login con el UsuarioDAO para validar credenciales.
    """

    def __init__(self):
        self.usuario_dao = UsuarioDAO()
        self.usuario_actual: Usuario | None = None

    def login(self, nombre_usuario: str, clave: str) -> tuple[bool, str]:
        """Intenta autenticar al usuario.

        Args:
            nombre_usuario: Nombre de usuario ingresado.
            clave: Contraseña en texto plano ingresada.

        Returns:
            Tupla (éxito: bool, mensaje: str).
            Si éxito es True, self.usuario_actual queda seteado con el Usuario autenticado.
        """
        # Validaciones básicas de campos vacíos
        if not nombre_usuario or not nombre_usuario.strip():
            return False, "El campo de usuario no puede estar vacío."

        if not clave or not clave.strip():
            return False, "El campo de contraseña no puede estar vacío."

        nombre_usuario = nombre_usuario.strip()
        clave = clave.strip()

        try:
            usuario = self.usuario_dao.validar_credenciales(nombre_usuario, clave)

            if usuario is not None:
                self.usuario_actual = usuario
                return True, f"Bienvenido/a, {usuario.nombre} {usuario.apellido}."

            return False, "Usuario o contraseña incorrectos."

        except Exception as e:
            return False, f"Error al conectar con la base de datos: {str(e)}"

    def logout(self):
        """Cierra la sesión del usuario actual."""
        self.usuario_actual = None

    def obtener_usuario_actual(self) -> Usuario | None:
        """Retorna el usuario autenticado actualmente, o None si no hay sesión."""
        return self.usuario_actual
