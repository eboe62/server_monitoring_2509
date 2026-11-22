"""Esquema de log_type (B10-1): el número ordena por gravedad.

Hasta 05 nadie ha entrado; desde 06, sí. Se lee el código sin importarlo
(los ingestores necesitan la BBDD y el entorno del contenedor).
"""
import ast
import pathlib
import re

INGEST = pathlib.Path("src/log_ingestor/log_ingest_batch.py")
FUNCTIONS = pathlib.Path("ops/services/postgres/init/02_functions.sql")
ALERT_RISK = pathlib.Path("src/log_ingestor/alert_risk.py")
ENTRY_TYPES = {"06_login_accepted"}


def _pattern_names():
    tree = ast.parse(INGEST.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "pattern_names" for t in node.targets
        ):
            return [e.value for e in node.value.elts]
    raise AssertionError("pattern_names no encontrado")


def test_only_entries_from_06():
    for name in _pattern_names():
        number = int(name.split("_", 1)[0])
        assert (number >= 6) == (name in ENTRY_TYPES), name


def test_old_name_gone_from_code():
    for path in (INGEST, FUNCTIONS, ALERT_RISK):
        text = path.read_text(encoding="utf-8")
        assert "08_connection_out" not in text, path
        assert "05_connection_in" not in text, path


def test_honeypot_ranking_covers_every_attacking_type():
    ranked = set(re.findall(r"WHEN '([0-9]{2}_[a-z_]+)' THEN", FUNCTIONS.read_text(encoding="utf-8")))
    assert set(_pattern_names()) <= ranked
