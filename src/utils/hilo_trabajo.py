"""
Utilidad de ejecución en hilo secundario para SGI Salud.

Permite ejecutar tareas de I/O (consultas a BD, lectura de disco) en un hilo
daemon separado, devolviendo el resultado al hilo principal de Tkinter
mediante widget.after().

Uso:
    from utils.hilo_trabajo import ejecutar_en_hilo

    ejecutar_en_hilo(
        self,  # cualquier widget Tkinter
        tarea=lambda: self.controlador.listar_pacientes(),
        callback_exito=self._on_datos_cargados,
        callback_error=lambda e: self._mostrar_mensaje(str(e), True),
    )
"""

import threading
from loguru import logger


def ejecutar_en_hilo(widget_tk, tarea, callback_exito, callback_error=None):
    """Ejecuta una tarea en un hilo daemon y devuelve el resultado al hilo principal.

    La tarea (callable sin argumentos) se ejecuta en un hilo secundario.
    Al completarse, el resultado se envía al hilo de Tkinter mediante
    widget.after(0, callback), garantizando seguridad de hilos.

    Args:
        widget_tk:      Cualquier widget de Tkinter (se usa .after() para
                        devolver el resultado al hilo principal).
        tarea:          Callable sin argumentos que retorna un resultado.
                        Se ejecuta en el hilo secundario.
        callback_exito: Callable(resultado) invocado en el hilo principal
                        con el valor retornado por tarea().
        callback_error: Callable(excepcion) invocado en el hilo principal
                        si tarea() lanza una excepción. Opcional.
    """
    def _worker():
        try:
            resultado = tarea()
            widget_tk.after(0, lambda r=resultado: callback_exito(r))
        except Exception as e:
            logger.error(f"Error en hilo de trabajo: {e}")
            if callback_error:
                widget_tk.after(0, lambda err=e: callback_error(err))

    hilo = threading.Thread(target=_worker, daemon=True)
    hilo.start()
    return hilo
