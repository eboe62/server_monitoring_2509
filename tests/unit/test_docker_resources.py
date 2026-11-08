"""docker_resources (B5a): parseo y evaluación de stats/inspect por stdin. Sin Docker ni SMTP."""
import json

from resource_monitor import docker_resources as dr


def _stats(name, cpu, mem):
    return json.dumps({"Name": name, "CPUPerc": cpu, "MemUsage": mem, "MemPerc": "x"})


def _limits(name, cpus, mem_bytes=0):
    return json.dumps({"Name": f"/{name}", "NanoCpus": int(cpus * 1e9), "Memory": mem_bytes})


def test_to_megabytes_unidades():
    assert dr.to_megabytes("128MiB") == 128
    assert dr.to_megabytes("1.5GiB") == 1536
    assert dr.to_megabytes("512KiB") == 0.5
    assert dr.to_megabytes("0B") == 0
    assert dr.to_megabytes("raro") == 0


def test_parse_memory_y_porcentaje():
    assert dr.parse_memory("64.47MiB / 128MiB") == (64.47, 128)
    assert dr.parse_memory("--") == (0.0, 0.0)
    assert dr.parse_percentage("0.33%") == 0.33
    assert dr.parse_percentage("--") == 0.0


def test_read_input_separa_stats_y_limites():
    lines = [_stats("loki", "0.33%", "95.8MiB / 500MiB"), _limits("loki", 0.5), "", "no json"]
    stats, limits = dr.read_input(lines)
    assert list(stats) == ["loki"] and list(limits) == ["loki"]   # quita la "/" de inspect


def test_cpu_se_mide_sobre_el_limite():
    # 22 % de un núcleo con límite 0.25 CPUs = 88 % de su techo -> alerta
    stats, limits = dr.read_input([_stats("cron", "22%", "40MiB / 256MiB"), _limits("cron", 0.25)])
    rows, alerts = dr.evaluate(stats, limits)
    assert round(rows[0]["CPU_pct"]) == 88
    assert [a["Name"] for a in alerts] == ["cron"]


def test_memoria_por_encima_del_umbral():
    stats, limits = dr.read_input([
        _stats("postgres", "0.0%", "450MiB / 500MiB"), _limits("postgres", 0.5),
        _stats("grafana", "0.04%", "163.9MiB / 300MiB"), _limits("grafana", 0.3),
    ])
    rows, alerts = dr.evaluate(stats, limits)
    assert [r["Name"] for r in rows] == ["grafana", "postgres"]
    assert [a["Name"] for a in alerts] == ["postgres"]


def test_sin_limite_de_cpu_compara_con_un_nucleo():
    stats, _ = dr.read_input([_stats("x", "50%", "10MiB / 100MiB")])
    rows, alerts = dr.evaluate(stats, {})
    assert rows[0]["CPU_limit"] == "sin límite" and rows[0]["CPU_pct"] == 50 and alerts == []


def test_tabla_y_html():
    stats, limits = dr.read_input([_stats("postgres", "0%", "450MiB / 500MiB"), _limits("postgres", 0.5)])
    rows, alerts = dr.evaluate(stats, limits)
    assert "postgres" in dr.build_table(rows) and "⚠️" in dr.build_table(rows)
    assert "<td>postgres</td>" in dr.build_html_report(alerts)


def test_sin_stdin_explica_como_ejecutarlo(capsys):
    assert dr.main([]) == 2
    assert "make docker-resources" in capsys.readouterr().err
