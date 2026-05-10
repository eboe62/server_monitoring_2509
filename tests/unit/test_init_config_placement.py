import glob
import re

import pytest

ENTRYPOINT_DIR = "src/log_ingestor"

def test_init_config_calls_are_in_main_block():
    """Verifica que las llamadas a init_config(...) aparezcan únicamente
    dentro de bloques `if __name__ == "__main__":` en los entrypoints.
    """
    pattern = re.compile(r"init_config\([^)]*\)")
    main_marker = re.compile(r"if __name__ == \"__main__\":")

    files = glob.glob(f"{ENTRYPOINT_DIR}/*.py")
    offending = []
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read()
        for m in pattern.finditer(text):
            idx = m.start()
            # Check if there's a main_marker before this position
            before = text[:idx]
            if not main_marker.search(before):
                offending.append((fp, m.group(0)))
    assert not offending, f"init_config() found outside __main__ in files: {offending}"
