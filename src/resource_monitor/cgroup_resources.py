#!/usr/bin/env python3
# cgroup_resources.py
"""
Recursos de los contenedores leídos del kernel (cgroup v2), para el correo diario (B5b).

Sin Docker: el cron monta en solo lectura /sys/fs/cgroup/system.slice -> /host/cgroup
(excepción auditada, ADR-0031 §2). Cada contenedor es una carpeta docker-<id>.scope con:

  memory.current   memoria en uso (bytes)
  memory.peak      máximo alcanzado desde que arrancó (bytes)
  memory.max       límite (bytes, o "max" si no hay)
  memory.events    línea "oom_kill N": veces que el kernel ha matado un proceso por memoria
  cpu.stat         "nr_throttled" y "throttled_usec": cuánto le ha frenado su límite de CPU

Los contadores empiezan en 0 cada vez que el contenedor arranca.
El kernel solo conoce el id; el nombre sale de containers.map, que escribe el host al final
de make deploy (docker ps --no-trunc). Si falta, se muestra el id corto.
"""
import html
import os
from datetime import datetime, timezone

CGROUP_ROOT = os.environ.get("CGROUP_ROOT", "/host/cgroup")
CONTAINERS_MAP = os.environ.get("CONTAINERS_MAP", "/host/runtime/containers.map")

THRESHOLD_PEAK = 80.0   # % del límite de memoria alcanzado en el pico
RESTART_MARGIN_S = 300  # arranque > 5 min después del mapa del deploy = reinicio no planificado

_MIB = 1024 * 1024


# ==========================================
# Lectura (tolerante: un fichero que falta no rompe el correo)
# ==========================================

def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_kv(text):
    """'oom 0\\noom_kill 2' -> {'oom': 0, 'oom_kill': 2}"""
    out = {}
    for line in (text or "").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("-").isdigit():
            out[parts[0]] = int(parts[1])
    return out


def load_container_map(path=CONTAINERS_MAP):
    """'<id completo> <nombre>' por línea -> ({id: nombre}, fecha del fichero o None)."""
    text = _read(path)
    if text is None:
        return {}, None
    mapping = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            mapping[parts[0]] = parts[1]
    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
    return mapping, mtime


def read_scope(scope_dir):
    """Lee una carpeta docker-<id>.scope. Valores en bytes / microsegundos (None si falta)."""
    events = parse_kv(_read(os.path.join(scope_dir, "memory.events")))
    cpu = parse_kv(_read(os.path.join(scope_dir, "cpu.stat")))
    max_raw = _read(os.path.join(scope_dir, "memory.max"))
    try:
        started = datetime.fromtimestamp(os.path.getmtime(scope_dir), tz=timezone.utc)
    except OSError:
        started = None
    return {
        "mem_current": _to_int(_read(os.path.join(scope_dir, "memory.current"))),
        "mem_peak": _to_int(_read(os.path.join(scope_dir, "memory.peak"))),
        "mem_max": None if max_raw in (None, "max") else _to_int(max_raw),
        "oom_kill": events.get("oom_kill", 0),
        "nr_throttled": cpu.get("nr_throttled", 0),
        "throttled_usec": cpu.get("throttled_usec", 0),
        "started": started,
    }


def collect(root=CGROUP_ROOT, map_path=CONTAINERS_MAP):
    """
    Devuelve (filas, fecha_del_mapa) o (None, None) si el montaje no existe.
    Cada fila: name, mem_current/peak/max (MiB), peak_pct, oom_kill, throttled_s, started,
    restarted (bool) y alert (bool).
    """
    if not os.path.isdir(root):
        return None, None
    mapping, map_time = load_container_map(map_path)
    rows = []
    for entry in sorted(os.listdir(root)):
        if not (entry.startswith("docker-") and entry.endswith(".scope")):
            continue
        cid = entry[len("docker-"):-len(".scope")]
        rows.append(evaluate(mapping.get(cid, cid[:12]), read_scope(os.path.join(root, entry)), map_time))
    rows.sort(key=lambda r: r["name"])
    return rows, map_time


def evaluate(name, raw, map_time):
    """Pasa una lectura cruda a MiB / % y marca alertas. Función pura."""
    def mib(v):
        return v / _MIB if v is not None else None

    peak = raw["mem_peak"] if raw["mem_peak"] is not None else raw["mem_current"]
    peak_pct = (peak / raw["mem_max"] * 100) if (peak is not None and raw["mem_max"]) else None
    started = raw["started"]
    restarted = bool(
        map_time and started and (started - map_time).total_seconds() > RESTART_MARGIN_S
    )
    return {
        "name": name,
        "mem_current": mib(raw["mem_current"]),
        "mem_peak": mib(peak),
        "mem_max": mib(raw["mem_max"]),
        "peak_pct": peak_pct,
        "oom_kill": raw["oom_kill"],
        "throttled_s": raw["throttled_usec"] / 1e6,
        "started": started,
        "restarted": restarted,
        "alert": raw["oom_kill"] > 0 or restarted or (peak_pct is not None and peak_pct > THRESHOLD_PEAK),
    }


def count_oom(rows):
    """Contenedores con algún OOM kill (o reiniciados sin deploy: el OOM de su proceso principal
    borra los contadores al rearrancar, el reinicio es la única huella que queda)."""
    return sum(1 for r in (rows or []) if r["oom_kill"] > 0 or r["restarted"])


# ==========================================
# HTML para el correo
# ==========================================

def _fmt(v, pattern="{:.1f}"):
    return pattern.format(v) if v is not None else "—"


def build_html(rows, map_time):
    if rows is None:
        return (
            "<h3 style='color:#7f8c8d;'>📊 Recursos de los contenedores</h3>"
            "<p style='color:#7f8c8d;'>No disponible: falta el montaje /host/cgroup (ADR-0031 §2).</p>"
        )
    deploy_txt = map_time.strftime("%Y-%m-%d %H:%M UTC") if map_time else "desconocido"
    parts = [
        "<h3 style='color:#2c3e50;'>📊 Recursos de los contenedores</h3>",
        "<p style='color:#555;'>Datos del kernel desde el último arranque de cada contenedor "
        f"(último deploy: {deploy_txt}). En rojo: pico &gt; {THRESHOLD_PEAK:.0f} % del límite, "
        "OOM o reinicio sin deploy.</p>",
        "<table border='1' cellpadding='4' cellspacing='0' style='border-collapse: collapse;'>",
        "<tr style='background-color:#f2f2f2;'><th>Contenedor</th><th>Mem MiB</th><th>Pico MiB</th>"
        "<th>Límite MiB</th><th>Pico %</th><th>OOM</th><th>CPU frenada (s)</th><th>Arrancó</th></tr>",
    ]
    for r in rows:
        style = " style='color:#c0392b;font-weight:bold;'" if r["alert"] else ""
        started = r["started"].strftime("%m-%d %H:%M") if r["started"] else "—"
        if r["restarted"]:
            started += " ⚠️"
        parts.append(
            f"<tr{style}><td>{html.escape(r['name'])}</td><td>{_fmt(r['mem_current'])}</td><td>{_fmt(r['mem_peak'])}</td>"
            f"<td>{_fmt(r['mem_max'])}</td><td>{_fmt(r['peak_pct'], '{:.0f} %')}</td>"
            f"<td>{r['oom_kill']}</td><td>{r['throttled_s']:.1f}</td><td>{started}</td></tr>"
        )
    parts.append("</table>")
    return "\n".join(parts)
