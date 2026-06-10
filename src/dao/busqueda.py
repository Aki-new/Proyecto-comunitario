"""
DAO de búsqueda sobre la vista combinada paciente-tarjeta-color.

Ejecuta consultas sobre `vista_paciente_tarjeta` para la búsqueda
de pacientes con sus tarjetas y colores asociados.

Cambios v3:
    - Búsqueda por nombre_completo mejorada: soporta múltiples palabras
      buscando cada palabra en TODOS los campos de nombre y apellido.
    - Todas las búsquedas son case-insensitive gracias a COLLATE NOCASE.
    - Añadida búsqueda por num_historia.
    - Resultados ordenados por apellido1, nombre1 por defecto.
    - Soporte para paginación (LIMIT, OFFSET) en DB.
    - Optimizaciones usando FTS5 para texto.
"""

import sqlite3
from models.busqueda import TarjetaSalida
from dao.conexion import ConexionDB
from utils.date_utils import formatear_fecha_para_mostrar, normalizar_fecha_para_busqueda, generar_patrones_busqueda_fecha

class BusquedaDAO:
    """DAO para consultas sobre la vista 'vista_paciente_tarjeta'."""

    _ORDEN = " ORDER BY apellido1, nombre1"

    def __init__(self):
        self.db = ConexionDB()

    def _ejecutar_consulta(self, select_clause: str, from_where_clause: str, params: tuple = (), limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Ejecuta una consulta SQL, cuenta totales y mapea filas a TarjetaSalida."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        
        # 1. Contar totales
        count_query = f"SELECT COUNT(*) {from_where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 2. Ejecutar consulta paginada
        query = f"{select_clause} {from_where_clause}{self._ORDEN}"
        if limit is not None:
            query += f" LIMIT {limit}"
        if offset is not None:
            query += f" OFFSET {offset}"

        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        filas = cursor.fetchall()
        conn.close()

        resultados = []
        for fila in filas:
            datos = dict(fila)
            if datos.get("fecha_nacimiento"):
                datos["fecha_nacimiento"] = formatear_fecha_para_mostrar(datos["fecha_nacimiento"])
            resultados.append(TarjetaSalida(**datos))
        return resultados, total

    # ══════════════════════════════════════════════════════════════════
    #  CONSULTAS
    # ══════════════════════════════════════════════════════════════════

    def obtener_todos(self, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Retorna todos los registros de la vista, paginados."""
        return self._ejecutar_consulta(
            "SELECT *",
            "FROM vista_paciente_tarjeta",
            (), limit, offset
        )

    def buscar_por_cedula(self, cedula: str, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda por cédula usando FTS5."""
        v = cedula.replace("'", "''").replace('"', '""')
        return self._ejecutar_consulta(
            "SELECT v.*",
            "FROM vista_paciente_tarjeta v JOIN pacientes_fts fts ON v.id_paciente = fts.id_paciente WHERE fts.cedula MATCH ?",
            (f'"{v}"',), limit, offset
        )

    def buscar_por_nombre(self, nombre: str, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda por nombre completo usando FTS5."""
        v = nombre.replace("'", "''").replace('"', '""')
        return self._ejecutar_consulta(
            "SELECT v.*",
            "FROM vista_paciente_tarjeta v JOIN pacientes_fts fts ON v.id_paciente = fts.id_paciente WHERE fts.nombres MATCH ?",
            (f'"{v}"',), limit, offset
        )

    def buscar_por_apellido(self, apellido: str, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda por apellido completo usando FTS5."""
        v = apellido.replace("'", "''").replace('"', '""')
        return self._ejecutar_consulta(
            "SELECT v.*",
            "FROM vista_paciente_tarjeta v JOIN pacientes_fts fts ON v.id_paciente = fts.id_paciente WHERE fts.apellidos MATCH ?",
            (f'"{v}"',), limit, offset
        )

    def buscar_por_nombre_completo(self, texto: str, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda inteligente multi-palabra usando FTS5."""
        palabras = texto.strip().split()
        if not palabras:
            return self.obtener_todos(limit, offset)

        match_query = " ".join([f'"{p}"' for p in palabras])
        return self._ejecutar_consulta(
            "SELECT v.*",
            "FROM vista_paciente_tarjeta v JOIN pacientes_fts fts ON v.id_paciente = fts.id_paciente WHERE fts MATCH ?",
            (match_query,), limit, offset
        )

    def buscar_por_fecha_nacimiento(self, fecha: str, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda por fecha de nacimiento (parcial o exacta)."""
        valores = generar_patrones_busqueda_fecha(fecha)
        if not valores:
            return [], 0

        placeholders = " OR ".join(["fecha_nacimiento LIKE ?"] * len(valores))
        params = tuple(f"%{valor}%" for valor in valores)
        return self._ejecutar_consulta(
            "SELECT *",
            f"FROM vista_paciente_tarjeta WHERE ({placeholders})",
            params, limit, offset
        )

    def buscar_por_lugar_nacimiento(self, lugar: str, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda parcial por lugar de nacimiento (case-insensitive)."""
        return self._ejecutar_consulta(
            "SELECT *",
            "FROM vista_paciente_tarjeta WHERE lugar_nacimiento LIKE ? COLLATE NOCASE",
            (f"%{lugar}%",), limit, offset
        )

    def buscar_por_num_historia(self, num_historia: str, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda parcial por número de historia."""
        return self._ejecutar_consulta(
            "SELECT *",
            "FROM vista_paciente_tarjeta WHERE num_historia LIKE ?",
            (f"%{num_historia}%",), limit, offset
        )

    def buscar_multicriterio(self, filtros: dict, limit: int = None, offset: int = None) -> tuple[list[TarjetaSalida], int]:
        """Búsqueda avanzada multi-criterio combinando filtros con AND."""
        if not filtros:
            return self.obtener_todos(limit, offset)

        condiciones = []
        parametros = []
        
        # Evaluar si usamos FTS5
        usar_fts = False
        fts_match_parts = []

        v_cedula = filtros.get("cedula", "")
        if v_cedula and str(v_cedula).strip():
            usar_fts = True
            v = str(v_cedula).strip().replace('"', '""')
            fts_match_parts.append(f'cedula: "{v}"')
            
        v_nombre = filtros.get("nombre", "")
        if v_nombre and str(v_nombre).strip():
            usar_fts = True
            v = str(v_nombre).strip().replace('"', '""')
            fts_match_parts.append(f'nombres: "{v}"')
            
        v_apellido = filtros.get("apellido", "")
        if v_apellido and str(v_apellido).strip():
            usar_fts = True
            v = str(v_apellido).strip().replace('"', '""')
            fts_match_parts.append(f'apellidos: "{v}"')
            
        if usar_fts and fts_match_parts:
            condiciones.append("fts MATCH ?")
            parametros.append(" AND ".join(fts_match_parts))

        for clave, valor in filtros.items():
            if valor is None or clave in ["cedula", "nombre", "apellido"]:
                continue

            if clave == "lugar_nacimiento":
                v = str(valor).strip()
                if v:
                    condiciones.append("v.lugar_nacimiento LIKE ? COLLATE NOCASE")
                    parametros.append(f"%{v}%")

            elif clave == "fecha_nacimiento":
                v = str(valor).strip()
                if v:
                    valores = generar_patrones_busqueda_fecha(v)
                    if valores:
                        condiciones.append("(" + " OR ".join(["v.fecha_nacimiento LIKE ?"] * len(valores)) + ")")
                        parametros.extend(f"%{valor_busqueda}%" for valor_busqueda in valores)

            elif clave == "fecha_nacimiento_partes":
                dia, mes, anio = valor
                if dia and str(dia).strip():
                    try:
                        condiciones.append("strftime('%d', v.fecha_nacimiento) = ?")
                        parametros.append(f"{int(dia):02d}")
                    except ValueError: pass
                if mes and str(mes).strip():
                    try:
                        condiciones.append("strftime('%m', v.fecha_nacimiento) = ?")
                        parametros.append(f"{int(mes):02d}")
                    except ValueError: pass
                if anio and str(anio).strip():
                    try:
                        condiciones.append("strftime('%Y', v.fecha_nacimiento) = ?")
                        parametros.append(f"{int(anio):04d}")
                    except ValueError: pass

        if not condiciones:
            return self.obtener_todos(limit, offset)

        where = " AND ".join(condiciones)
        
        if usar_fts:
            from_where = f"FROM vista_paciente_tarjeta v JOIN pacientes_fts fts ON v.id_paciente = fts.id_paciente WHERE {where}"
            select = "SELECT v.*"
        else:
            from_where = f"FROM vista_paciente_tarjeta v WHERE {where}"
            select = "SELECT v.*"
            
        return self._ejecutar_consulta(select, from_where, tuple(parametros), limit, offset)
