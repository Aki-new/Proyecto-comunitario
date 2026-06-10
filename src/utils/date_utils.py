from __future__ import annotations

from datetime import datetime, date
from typing import Optional

ACCEPTED_DATE_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]


def parse_date(fecha: str) -> date:
    """Parses a date string in DD/MM/YYYY, DD-MM-YYYY or YYYY-MM-DD."""
    if fecha is None:
        raise ValueError("Fecha no puede ser None")

    fecha_str = str(fecha).strip()
    if not fecha_str:
        raise ValueError("Fecha no puede estar vacia")

    for fmt in ACCEPTED_DATE_FORMATS:
        try:
            return datetime.strptime(fecha_str, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        "Formato de fecha invalido. Use DD/MM/YYYY, DD-MM-YYYY o YYYY-MM-DD."
    )


def normalizar_fecha_a_iso(fecha: str) -> str:
    """Normaliza una fecha de entrada a YYYY-MM-DD para almacenamiento."""
    fecha_dt = parse_date(fecha)
    if fecha_dt.year < 1900 or fecha_dt.year > 2100:
        raise ValueError("Anio invalido (debe ser 1900-2100).")
    return fecha_dt.strftime("%Y-%m-%d")


def formatear_fecha_para_mostrar(fecha: str | date) -> str:
    """Formatea una fecha a DD-MM-YYYY para mostrar en la UI."""
    if isinstance(fecha, str):
        fecha_dt = parse_date(fecha)
    else:
        fecha_dt = fecha
    return fecha_dt.strftime("%d-%m-%Y")


def formatear_fecha_para_entrada(fecha: str | date, separador: str = "-") -> str:
    """Formatea una fecha a DD-MM-YYYY o DD/MM/YYYY para colocar en inputs."""
    if isinstance(fecha, str):
        fecha_dt = parse_date(fecha)
    else:
        fecha_dt = fecha
    sep = "/" if separador == "/" else "-"
    return fecha_dt.strftime(f"%d{sep}%m{sep}%Y")


def normalizar_fecha_para_busqueda(fecha: str) -> str:
    """Si el usuario ingresó una fecha completa como DD-MM-YYYY o DD/MM/YYYY,
    la convierte a YYYY-MM-DD para buscar en la base de datos.
    Si no es una fecha completa válida, retorna el valor original.
    """
    try:
        return normalizar_fecha_a_iso(fecha)
    except ValueError:
        return fecha.strip()


def generar_patrones_busqueda_fecha(fecha: str) -> list[str]:
    """Genera patrones de búsqueda para una fecha completa o parcial.

    Para fechas completas, devuelve patrones en ISO y en formatos de usuario
    con guiones y barras.
    """
    valor = str(fecha).strip()
    if not valor:
        return []

    try:
        iso = normalizar_fecha_a_iso(valor)
        dash = formatear_fecha_para_mostrar(iso)
        slash = dash.replace("-", "/")
        return [iso, dash, slash]
    except ValueError:
        return [valor]
