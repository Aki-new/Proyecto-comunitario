import sys
from loguru import logger


def inicializar_logs():
    # Remover la configuración por defecto de loguru
    logger.remove()

    # 1. Log en Consola (Bonito y coloreado para desarrollo)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        enqueue=True
    )

    # 2. Log en Archivo (Rotativo y persistente para depurar fallos en producción)
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        encoding="utf-8",
        enqueue=True
    )
