#!/usr/bin/env python3
import os
from typing import Optional
from .utils import log_info

def load_secret(secret_file_env: str, fallback_env: Optional[str] = None) -> Optional[str]:
    """Carga un secreto siguiendo la convención *_FILE con reglas de fallback seguras.

    Comportamiento:
    - Si existe la variable de entorno `secret_file_env` y el fichero existe, devuelve su contenido (strip).
    - Si no existe fichero y `fallback_env` está proporcionada, devuelve la variable de entorno
      solo si no se ejecuta en producción o si `ALLOW_INSECURE_ENV_SECRETS=true`.
    - En producción, el uso del fallback a variable de entorno sin fichero está prohibido
      por defecto y lanzará RuntimeError para evitar exposición accidental de secretos.

    Devuelve la cadena del secreto o None si no se encuentra (o lanza en fallback prohibido).
    """
    file_path = os.getenv(secret_file_env)

    if file_path:
        try:
            if os.path.exists(file_path):
                with open(file_path) as f:
                    return f.read().strip()
            else:
                log_info(f"[WARN] {secret_file_env} definido pero fichero no encontrado: {file_path}")
        except Exception as e:
            log_info(f"[WARN] Error leyendo fichero secreto {file_path}: {e}")

    # Fallback a variable de entorno
    if fallback_env:
        fallback_val = os.getenv(fallback_env)
        if fallback_val is None:
            return None

        env = os.getenv("ENVIRONMENT", "development").lower()
        allow_insecure = os.getenv("ALLOW_INSECURE_ENV_SECRETS", "false").lower() == "true"

        if env == "production" and not allow_insecure:
            msg = (
                f"En producción, el fallback a la variable {fallback_env} está prohibido salvo "
                "ALLOW_INSECURE_ENV_SECRETS=true"
            )
            log_info(f"[ERROR] {msg}")
            raise RuntimeError(msg)

        log_info(f"[WARN] Usando fallback a variable de entorno {fallback_env}; considerar usar secreto basado en fichero")
        return fallback_val

    return None
