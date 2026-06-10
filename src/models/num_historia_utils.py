"""
Utilidades para el manejo del número de historia clínica.

Formato: XX-XX-XX (3 pares de dígitos separados por guiones).
El último par determina automáticamente el color de la tarjeta.
"""

import re

# ── Patrón de validación: 3 pares de dígitos (00-99) separados por guiones ──
PATRON_NUM_HISTORIA = re.compile(r"^\d{2}-\d{2}-\d{2}$")

# ── Mapa de colores según la decena del último par ───────────────────────────
# Clave: decena (0-9), Valor: (nombre_color, código_hex)
MAPA_COLORES = {
    0: ("Marron",       "#8B4513"),
    1: ("Azul Marino",  "#000080"),
    2: ("Verde",        "#228B22"),
    3: ("Naranja",      "#FF8C00"),
    4: ("Morado",       "#800080"),
    5: ("Rosa",         "#FF69B4"),
    6: ("Turquesa",     "#40E0D0"),
    7: ("Amarillo",     "#FFD700"),
    8: ("Rojo",         "#DC143C"),
    9: ("Azul Celeste", "#87CEEB"),
}

# ── Lista ordenada de colores para referencia ────────────────────────────────
LISTA_COLORES = [
    {"rango": "00-09", "nombre": "Marron",       "hex": "#8B4513"},
    {"rango": "10-19", "nombre": "Azul Marino",  "hex": "#000080"},
    {"rango": "20-29", "nombre": "Verde",        "hex": "#228B22"},
    {"rango": "30-39", "nombre": "Naranja",      "hex": "#FF8C00"},
    {"rango": "40-49", "nombre": "Morado",       "hex": "#800080"},
    {"rango": "50-59", "nombre": "Rosa",         "hex": "#FF69B4"},
    {"rango": "60-69", "nombre": "Turquesa",     "hex": "#40E0D0"},
    {"rango": "70-79", "nombre": "Amarillo",     "hex": "#FFD700"},
    {"rango": "80-89", "nombre": "Rojo",         "hex": "#DC143C"},
    {"rango": "90-99", "nombre": "Azul Celeste", "hex": "#87CEEB"},
]


def validar_formato_num_historia(valor: str) -> bool:
    """Verifica que el número de historia tenga formato XX-XX-XX.

    Args:
        valor: Cadena a validar.

    Returns:
        True si el formato es válido.
    """
    return bool(PATRON_NUM_HISTORIA.match(valor))


def obtener_color_por_num_historia(num_historia: str) -> dict:
    """Determina el color a partir del último par del número de historia.

    Args:
        num_historia: Número de historia en formato XX-XX-XX.

    Returns:
        Diccionario con 'nombre' y 'hex' del color.

    Raises:
        ValueError: Si el formato es inválido.
    """
    if not validar_formato_num_historia(num_historia):
        raise ValueError(
            f"Formato de numero de historia invalido: '{num_historia}'. "
            f"Debe ser XX-XX-XX (ej: 03-77-34)."
        )

    ultimo_par = num_historia.split("-")[2]
    decena = int(ultimo_par[0])  # Primer dígito = decena

    nombre, hex_color = MAPA_COLORES[decena]
    return {"nombre": nombre, "hex": hex_color}


def obtener_nombre_color(num_historia: str) -> str:
    """Atajo: retorna solo el nombre del color para un número de historia.

    Args:
        num_historia: Número de historia en formato XX-XX-XX.

    Returns:
        Nombre del color (ej: "Naranja").
    """
    return obtener_color_por_num_historia(num_historia)["nombre"]
