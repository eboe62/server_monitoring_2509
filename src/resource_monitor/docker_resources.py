#!/usr/bin/env python3
# docker_resources.py
"""
Consumo de CPU y memoria de cada contenedor frente a su límite (B5a).

Ejecución MANUAL desde el host (no hay job en el cron):

    make docker-resources

Reparto de papeles (ADR-0018 §1.6, ADR-0020, ADR-0031):
  - El HOST mide: `docker stats` + `docker inspect` (plano de control de Docker).
  - Este script EVALÚA: lee esas líneas JSON por stdin, dentro de monitoring-cron.
  El contenedor nunca habla con Docker: no hay docker.sock ni cliente docker.

Entrada (una línea JSON por contenedor, en cualquier orden):
  {"Name": "...", "CPUPerc": "0.33%", "MemUsage": "95.8MiB / 500MiB", ...}   <- docker stats
  {"Name": "/...", "NanoCpus": 500000000, "Memory": 524288000}              <- docker inspect

CPU: `docker stats` da el % de UN núcleo (100 % = 1 CPU). Con un límite de 0.25 CPUs el
techo real es 25 %, por eso aquí se calcula el % sobre el límite del contenedor.

Correo: solo si algún contenedor supera el umbral (cuota de correo limitada).
"""
import argparse
import html
import json
import sys

from monitoring.common.config import log_info, send_email, init_config

THRESHOLD_MEM = 80.0  # % del límite de memoria
THRESHOLD_CPU = 80.0  # % del límite de CPU

_UNITS = {
    "B": 1 / 1024 / 1024,
    "KIB": 1 / 1024, "MIB": 1, "GIB": 1024, "TIB": 1024 * 1024,
    "KB": 1000 / 1024 / 1024, "MB": 1000 * 1000 / 1024 / 1024, "GB": 1000 ** 3 / 1024 / 1024,
}


# ==========================================
# Parseo (funciones puras: se prueban sin Docker)
# ==========================================

def parse_percentage(value):
    """'45.6%' -> 45.6 ; vacío o '--' -> 0.0"""
    try:
        return float(str(value).strip().replace("%", ""))
    except (TypeError, ValueError):
        return 0.0


def to_megabytes(size_str):
    """'123.4MiB' / '1.2GiB' / '512KiB' / '0B' -> MiB (float)."""
    s = str(size_str).strip().upper()
    for unit in sorted(_UNITS, key=len, reverse=True):
        if s.endswith(unit):
            try:
                return float(s[: -len(unit)].strip()) * _UNITS[unit]
            except ValueError:
                return 0.0
    return 0.0


def parse_memory(mem_str):
    """'123.4MiB / 500MiB' -> (uso_MiB, limite_MiB)."""
    try:
        usage, limit = str(mem_str).split(" / ")
        return to_megabytes(usage), to_megabytes(limit)
    except ValueError:
        return 0.0, 0.0


def read_input(lines):
    """Separa las líneas JSON en (stats por nombre, límites por nombre)."""
    stats, limits = {}, {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            log_info(f"[WARN] Línea ignorada (no es JSON): {line[:80]}")
            continue
        name = str(data.get("Name", "")).lstrip("/")
        if not name:
            continue
        if "NanoCpus" in data:
            limits[name] = data
        elif "CPUPerc" in data:
            stats[name] = data
    return stats, limits


def evaluate(stats, limits):
    """Calcula cada fila y marca las que superan el umbral. Devuelve (filas, alertas)."""
    rows, alerts = [], []
    for name in sorted(stats):
        s = stats[name]
        cpu_core = parse_percentage(s.get("CPUPerc"))
        mem_usage, mem_limit = parse_memory(s.get("MemUsage"))
        mem_pct = (mem_usage / mem_limit * 100) if mem_limit > 0 else 0.0

        nano = (limits.get(name) or {}).get("NanoCpus") or 0
        cpu_limit = nano / 1e9 if nano else None
        # Sin límite de CPU se compara contra un núcleo (mejor que no comparar)
        cpu_pct = cpu_core / cpu_limit if cpu_limit else cpu_core

        row = {
            "Name": name,
            "CPU_limit": f"{cpu_limit:.2f}" if cpu_limit else "sin límite",
            "CPU_pct": cpu_pct,
            "MEM_usage": mem_usage,
            "MEM_limit": mem_limit,
            "MEM_pct": mem_pct,
            "alert": cpu_pct > THRESHOLD_CPU or mem_pct > THRESHOLD_MEM,
        }
        rows.append(row)
        if row["alert"]:
            alerts.append(row)
    return rows, alerts


# ==========================================
# Salida
# ==========================================

def build_table(rows):
    sep = "+-------------------------+------------+-----------+------------+------------+--------+"
    out = [
        sep,
        "| Contenedor              | CPUs lím.  | CPU % lím | Mem MiB    | Límite MiB | Mem %  |",
        sep,
    ]
    for r in rows:
        mark = "  ⚠️" if r["alert"] else ""
        out.append(
            f"| {r['Name']:<23} | {r['CPU_limit']:>10} | {r['CPU_pct']:>8.1f}% | "
            f"{r['MEM_usage']:>10.1f} | {r['MEM_limit']:>10.1f} | {r['MEM_pct']:>5.1f}% |{mark}"
        )
    out.append(sep)
    out.append(f"Umbral: {THRESHOLD_CPU:.0f} % del límite de CPU o {THRESHOLD_MEM:.0f} % del de memoria.")
    return "\n".join(out)


def build_html_report(alerts):
    parts = [
        "<html><body>",
        "<p><strong>⚠️ Contenedores cerca de su límite</strong> "
        f"(umbral {THRESHOLD_CPU:.0f} % CPU / {THRESHOLD_MEM:.0f} % memoria, sobre el límite de cada uno)</p>",
        "<table border='1' cellpadding='4' cellspacing='0' style='border-collapse: collapse;'>",
        "<tr style='background-color:#f2f2f2;'><th>Contenedor</th><th>CPUs lím.</th>"
        "<th>CPU % lím.</th><th>Mem MiB</th><th>Límite MiB</th><th>Mem %</th></tr>",
    ]
    for r in alerts:
        parts.append(
            f"<tr><td>{html.escape(r['Name'])}</td><td>{html.escape(r['CPU_limit'])}</td>"
            f"<td>{r['CPU_pct']:.1f}%</td><td>{r['MEM_usage']:.1f}</td>"
            f"<td>{r['MEM_limit']:.1f}</td><td>{r['MEM_pct']:.1f}%</td></tr>"
        )
    parts.append("</table>")
    parts.append(
        "<p style='color:#555;'>Si un contenedor llega a su límite de memoria, el kernel lo mata (OOM) "
        "y Docker lo reinicia sin avisar.</p>"
    )
    parts.append("</body></html>")
    return "\n".join(parts)


# ==========================================
# Proceso
# ==========================================

def main(argv=None):
    parser = argparse.ArgumentParser(description="Recursos de contenedores frente a su límite")
    parser.add_argument("--stdin", action="store_true", help="leer docker stats/inspect en JSON desde stdin")
    parser.add_argument("--no-email", action="store_true", help="solo mostrar la tabla, sin correo")
    args = parser.parse_args(argv)

    if not args.stdin or sys.stdin.isatty():
        print(
            "Este script no habla con Docker (no hay docker.sock en el contenedor).\n"
            "Ejecuta desde el host:  make docker-resources",
            file=sys.stderr,
        )
        return 2

    stats, limits = read_input(sys.stdin)
    if not stats:
        log_info("[ERROR] No han llegado datos de docker stats por stdin.")
        return 1

    rows, alerts = evaluate(stats, limits)
    print(build_table(rows))

    if not alerts:
        log_info(f"[OK] {len(rows)} contenedores por debajo del umbral.")
        return 0

    log_info(f"[WARN] {len(alerts)} contenedores por encima del umbral.")
    if args.no_email:
        return 0
    subject = f"⚠️ Recursos Docker: {len(alerts)} contenedores cerca del límite"
    if send_email(html_content=build_html_report(alerts), subject=subject):
        log_info(f"[📧]: Correo enviado: {subject}")
        return 0
    log_info("[ERROR] El envío del correo ha fallado (ver el log de send_email)")
    return 1


if __name__ == "__main__":
    init_config()
    sys.exit(main())
