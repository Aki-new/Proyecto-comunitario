from loguru import logger

logger.info("Log de informacion")
logger.trace("Log de rastro") # De inicio es ignorado
logger.debug("Log de debug")
logger.success("Log de exito")
logger.warning("Log de advertencia")
logger.error("Log de error")
logger.critical("Log de critical")

import sys

print()
print("Para que no ignore trace")
logger.remove(0)
logger.add(sys.stderr, level="TRACE") # Para que no ignore a Trace

logger.trace("Log de rastro")