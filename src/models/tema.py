"""
Sistema de temas visuales del SGI Salud.

Define 3 temas de colores (oscuro, claro, personalizado) y 4 tamaños de fuente.
Los temas se aplican dinámicamente en todas las vistas de la aplicación.

Uso:
    from models.tema import obtener_tema, obtener_tamano_fuente

    colores = obtener_tema("oscuro")        # → dict con todas las claves de color
    tamano  = obtener_tamano_fuente("grande") # → int (14)
"""

from models.config import AppConfig, ColoresPersonalizados


# ══════════════════════════════════════════════════════════════════
#  TEMAS DE COLORES
# ══════════════════════════════════════════════════════════════════

TEMA_OSCURO = {
    "fondo":             "#0F1923",
    "panel":             "#182633",
    "acento":            "#00A8E8",
    "acento_hover":      "#007BB5",
    "texto":             "#E8EDF2",
    "texto_secundario":  "#8899AA",
    "texto_tenue":       "#4A6275",
    "entrada_fondo":     "#1E3044",
    "entrada_borde":     "#2A4158",
    "error":             "#FF4C6A",
    "exito":             "#00D68F",
    "peligro":           "#FF4C6A",
    "peligro_hover":     "#D93A5A",
    "fila_alterna":      "#1A2D3D",
    "sidebar":           "#141E2B",
    "sidebar_borde":     "#1E3044",
    "header":            "#141E2B",
    "separador":         "#1E3044",
    "boton_hover":       "#1E3044",
}

TEMA_CLARO = {
    "fondo":             "#F0F2F5",
    "panel":             "#FFFFFF",
    "acento":            "#0078D4",
    "acento_hover":      "#005A9E",
    "texto":             "#1A1A2E",
    "texto_secundario":  "#5A6A7A",
    "texto_tenue":       "#9AA5B0",
    "entrada_fondo":     "#F5F7FA",
    "entrada_borde":     "#D0D7DE",
    "error":             "#D32F2F",
    "exito":             "#2E7D32",
    "peligro":           "#D32F2F",
    "peligro_hover":     "#B71C1C",
    "fila_alterna":      "#F0F4F8",
    "sidebar":           "#E8ECF0",
    "sidebar_borde":     "#D0D7DE",
    "header":            "#E8ECF0",
    "separador":         "#D0D7DE",
    "boton_hover":       "#E0E4E8",
}


def _colores_personalizados_a_tema(cp: ColoresPersonalizados) -> dict:
    """Convierte un objeto ColoresPersonalizados en un diccionario de tema completo.

    Los campos que no están en ColoresPersonalizados (sidebar, header, etc.)
    se derivan del color de fondo y panel.

    Args:
        cp: Colores definidos por el usuario.

    Returns:
        Diccionario con todas las claves de tema necesarias.
    """
    return {
        "fondo":             cp.fondo,
        "panel":             cp.panel,
        "acento":            cp.acento,
        "acento_hover":      cp.acento_hover,
        "texto":             cp.texto,
        "texto_secundario":  cp.texto_secundario,
        "texto_tenue":       cp.texto_secundario,
        "entrada_fondo":     cp.entrada_fondo,
        "entrada_borde":     cp.entrada_borde,
        "error":             cp.error,
        "exito":             cp.exito,
        "peligro":           cp.peligro,
        "peligro_hover":     cp.peligro_hover,
        "fila_alterna":      cp.fila_alterna,
        "sidebar":           cp.fondo,
        "sidebar_borde":     cp.entrada_borde,
        "header":            cp.fondo,
        "separador":         cp.entrada_borde,
        "boton_hover":       cp.entrada_fondo,
    }


def obtener_tema(config: AppConfig) -> dict:
    """Retorna el diccionario de colores según la configuración activa.

    Args:
        config: Configuración de la aplicación.

    Returns:
        Diccionario con claves: 'fondo', 'panel', 'acento', 'texto', etc.
    """
    if config.tema == "claro":
        return TEMA_CLARO.copy()
    elif config.tema == "personalizado":
        return _colores_personalizados_a_tema(config.colores_personalizados)
    else:
        return TEMA_OSCURO.copy()


# ══════════════════════════════════════════════════════════════════
#  TAMAÑOS DE FUENTE
# ══════════════════════════════════════════════════════════════════

TAMANOS_FUENTE = {
    "pequeno":    {"base": 10, "titulo": 14, "subtitulo": 12, "etiqueta": 9},
    "normal":     {"base": 12, "titulo": 16, "subtitulo": 14, "etiqueta": 11},
    "grande":     {"base": 14, "titulo": 18, "subtitulo": 16, "etiqueta": 13},
    "muy_grande": {"base": 16, "titulo": 20, "subtitulo": 18, "etiqueta": 15},
}


def obtener_tamano_fuente(config: AppConfig) -> dict:
    """Retorna los tamaños de fuente según la configuración activa.

    Args:
        config: Configuración de la aplicación.

    Returns:
        Diccionario con claves:
            'base':      Tamaño para texto normal (entries, labels, filas de tabla).
            'titulo':    Tamaño para títulos de sección.
            'subtitulo': Tamaño para subtítulos.
            'etiqueta':  Tamaño para etiquetas pequeñas (labels de formulario).
    """
    return TAMANOS_FUENTE.get(config.tamano_fuente, TAMANOS_FUENTE["normal"]).copy()
