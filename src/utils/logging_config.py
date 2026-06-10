import os
import sys
# pyrefly: ignore [missing-import]
from loguru import logger


def inicializar_logs():
    # Remover la configuración por defecto de loguru
    logger.remove()

    # 1. Log en Consola (Bonito y coloreado para desarrollo - solo si hay consola disponible)
    if sys.stderr is not None:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
            enqueue=True
        )

    # Calcular ruta absoluta del archivo de logs basada en la ubicación del archivo
    # Volver 3 niveles arriba: utils -> src -> raíz
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOG_PATH = os.path.join(BASE_DIR, "logs", "app.log")

    # Asegurar que el directorio de logs exista
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    # 2. Log en Archivo (Rotativo y persistente para depurar fallos en producción)
    logger.add(
        LOG_PATH,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        encoding="utf-8",
        enqueue=True
    )
