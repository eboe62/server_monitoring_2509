#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime
from common.utils import log_info, send_email

# Configuración
THRESHOLD_MEM = 80.0  # %
THRESHOLD_CPU = 80.0  # %
LOG_FILE = "/var/log/docker_resources_history.log"

def get_docker_stats():
    """Obtiene estadísticas de Docker en formato JSON."""
    cmd = ["docker", "stats", "--no-stream", "--format", "{{json .}}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stats_lines = result.stdout.strip().split("\n")
    return [json.loads(line) for line in stats_lines if line.strip()]

def parse_percentage(value):
    """Convierte '45.6%' en float."""
    return float(value.strip().replace('%', '')) if value else 0.0

def parse_memory(mem_str):
    """Convierte '123.4MiB / 500MiB' en (uso_MB, total_MB)."""
    try:
        usage, limit = mem_str.split(" / ")
        return to_megabytes(usage), to_megabytes(limit)
    except Exception:
        return (0.0, 0.0)

def to_megabytes(size_str):
    """Convierte tamaños como '123.4MiB' o '1.2GiB' a MB."""
    size_str = size_str.strip().upper()
    if size_str.endswith("MIB"):
        return float(size_str.replace("MIB", "").strip())
    elif size_str.endswith("GIB"):
        return float(size_str.replace("GIB", "").strip()) * 1024
    elif size_str.endswith("KIB"):
        return float(size_str.replace("KIB", "").strip()) / 1024
    return 0.0

def build_table(stats):
    lines = []
    lines.append("+--------------+------------+------------+------------+-----------------------------------------------------------+")
    lines.append("|    CPU %     |   MEM %    |   Uso_MB   |  Limite_MB |                         Contenedor                        |")
    lines.append("+--------------+------------+------------+------------+-----------------------------------------------------------+")
    for s in stats:
        lines.append(f"| {s['CPU']:<12} | {s['MEM%']:<10} | {s['Uso_MB']:<10} | {s['Limite_MB']:<10} | {s['Name']:<25} |")
    lines.append("+--------------+------------+------------+------------+-----------------------------------------------------------+")
    return "\n".join([f"mnt-info: {line}" for line in lines])

def build_html_report(alerts):
    # 3. Construir cuerpo del correo HTML
    # Genera informe HTML
    html_table = """
    <html>
    <body>
    <p><strong>Alerta de Recursos Docker:</strong></p>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th>CPU %</th>
                <th>Memoria %</th>
                <th>Uso</th>
                <th>Límite</th>
                <th>Contenedor</th>
            </tr>
        </thead>
        <tbody>
    """

    for row in alerts:
        html_table += f"""
            <tr>
                <td>{row['CPU']}</td>
                <td>{row['MEM%']}</td>
                <td>{row['Uso_MB']} MB</td>
                <td>{row['Limite_MB']} MB</td>
                <td>{row['Name']}</td>
            </tr>
        """

    html_table += """
        </tbody>
        </table>
        </body>
        </html>
    """
    return html_table

def log_stats(stats):
    with open(LOG_FILE, "a") as f:
        f.write(f"\nmnt-info: [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(build_table(stats))

def main():
    log_info("===== Inicio de ejecución =====")

    stats = get_docker_stats()
    processed_stats = []
    alerts = []

    for container in stats:
        cpu = parse_percentage(container["CPUPerc"])
        mem_usage, mem_limit = parse_memory(container["MemUsage"])
        mem_percent = (mem_usage / mem_limit * 100) if mem_limit > 0 else 0

        entry = {
            "CPU": f"{cpu:.1f}%",
            "MEM%": f"{mem_percent:.1f}%",
            "Uso_MB": f"{mem_usage:.1f}",
            "Limite_MB": f"{mem_limit:.1f}",
            "Name": container["Name"]
        }
        processed_stats.append(entry)

        if cpu > THRESHOLD_CPU or mem_percent > THRESHOLD_MEM:
            alerts.append(entry)

    # Guardar en log histórico
    log_stats(processed_stats)

    # Mostrar por stdout en tabla
    print(build_table(processed_stats))

    # Solo enviar email si hay contenedores en riesgo
    if alerts:
        log_info("⚠ Se han detectado contenedores en riesgo, enviando email...")
        html_report = build_html_report(alerts)
        send_email("🚨 Alerta: Recursos Docker al límite", html_report)
    else:
        log_info("No se han detectado contenedores en riesgo.")

    log_info("===== Fin de ejecución =====")

if __name__ == "__main__":
    main()

