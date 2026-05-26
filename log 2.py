from loguru import logger
import time
tiempo_inicio = time.perf_counter()

query = "query de prueba"
params = (1, 2, 4, 5, "jamon", "queso")

time.sleep(0.15)

tiempo_final = time.perf_counter()
tiempo_consulta = (tiempo_final - tiempo_inicio) * 1000
logger.success(f"""
        Consulta exitosa: 
        Query: {query}
        params: {params}
        tiempo: {tiempo_consulta} ms
    """
    )