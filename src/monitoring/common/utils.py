#!/usr/bin/env python3
import datetime

def log_info(msg: str) -> None:
    """Logger consistente para módulos de monitoring.

    Imprime una línea con marca temporal. Mantener implementación mínima
    para evitar dependencias pesadas en tiempo de ejecución del contenedor.
    """
    print(f"gda-info: {datetime.datetime.now().isoformat()} - {msg}")
