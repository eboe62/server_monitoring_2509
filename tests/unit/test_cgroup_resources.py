"""cgroup_resources (B5b): lectura de contadores del kernel con un árbol falso. Sin Docker."""
import os
import time
from datetime import datetime, timedelta, timezone

from log_ingestor import alert_risk as ar
from resource_monitor import cgroup_resources as cg

MIB = 1024 * 1024
CID_PG = "a" * 64
CID_CRON = "b" * 64


def _scope(root, cid, current, peak, limit, oom=0, throttled_usec=0):
    d = root / f"docker-{cid}.scope"
    d.mkdir()
    (d / "memory.current").write_text(f"{current}\n")
    if peak is not None:
        (d / "memory.peak").write_text(f"{peak}\n")
    (d / "memory.max").write_text(f"{limit}\n")
    (d / "memory.events").write_text(f"low 0\nhigh 0\nmax 0\noom 0\noom_kill {oom}\n")
    (d / "cpu.stat").write_text(f"usage_usec 999\nnr_throttled 3\nthrottled_usec {throttled_usec}\n")
    return d


def _tree(tmp_path, map_age_s=0):
    root = tmp_path / "cgroup"
    root.mkdir()
    (root / "init.scope").mkdir()   # otras carpetas del slice se ignoran
    _scope(root, CID_PG, 43 * MIB, 450 * MIB, 500 * MIB, oom=0, throttled_usec=2_500_000)
    _scope(root, CID_CRON, 30 * MIB, 40 * MIB, 256 * MIB, oom=1)
    mp = tmp_path / "containers.map"
    mp.write_text(f"{CID_PG} monitoring-postgres\n{CID_CRON} monitoring-cron\n")
    if map_age_s:
        t = time.time() - map_age_s
        os.utime(mp, (t, t))
    return str(root), str(mp)


def test_parse_kv():
    assert cg.parse_kv("oom 0\noom_kill 2\nraro\n") == {"oom": 0, "oom_kill": 2}
    assert cg.parse_kv(None) == {}


def test_collect_lee_nombres_pico_y_oom(tmp_path):
    root, mp = _tree(tmp_path)
    rows, map_time = cg.collect(root, mp)
    assert map_time is not None
    by = {r["name"]: r for r in rows}
    assert set(by) == {"monitoring-postgres", "monitoring-cron"}
    pg = by["monitoring-postgres"]
    assert round(pg["mem_peak"]) == 450 and round(pg["peak_pct"]) == 90 and pg["alert"]
    assert pg["throttled_s"] == 2.5
    assert by["monitoring-cron"]["oom_kill"] == 1 and by["monitoring-cron"]["alert"]
    assert cg.count_oom(rows) == 1


def test_sin_mapa_usa_id_corto_y_sin_limite(tmp_path):
    root = tmp_path / "cgroup"
    root.mkdir()
    d = _scope(root, CID_PG, 10 * MIB, None, "max")
    rows, map_time = cg.collect(str(root), str(tmp_path / "no-existe"))
    assert map_time is None
    r = rows[0]
    assert r["name"] == CID_PG[:12]
    assert r["mem_max"] is None and r["peak_pct"] is None and not r["alert"]
    assert round(r["mem_peak"]) == 10   # sin memory.peak: se usa el valor actual
    assert d.exists()


def test_reinicio_despues_del_deploy_cuenta_como_aviso():
    deploy = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)
    raw = {"mem_current": MIB, "mem_peak": MIB, "mem_max": 100 * MIB, "oom_kill": 0,
           "nr_throttled": 0, "throttled_usec": 0, "started": deploy + timedelta(hours=3)}
    assert cg.evaluate("x", raw, deploy)["restarted"]
    raw["started"] = deploy + timedelta(seconds=60)   # arranque dentro del propio deploy
    assert not cg.evaluate("x", raw, deploy)["restarted"]


def test_sin_montaje_no_rompe(tmp_path):
    assert cg.collect(str(tmp_path / "nada"), str(tmp_path / "map")) == (None, None)
    assert "No disponible" in cg.build_html(None, None)
    assert cg.count_oom(None) == 0


def test_html_marca_alertas(tmp_path):
    root, mp = _tree(tmp_path)
    rows, map_time = cg.collect(root, mp)
    body = cg.build_html(rows, map_time)
    assert "📊 Recursos" in body and "monitoring-postgres" in body and "#c0392b" in body


def test_asunto_con_oom():
    assert ar.build_subject(0, 500, 1) == "⚠️ Recursos: el kernel ha matado o reiniciado 1 contenedor"
    assert ar.build_subject(2, 500, 3).endswith("· ⚠️ el kernel ha matado o reiniciado 3 contenedores")
    assert ar.build_subject(0, 0, 1).startswith("⚠️ Monitorización: sin datos")
    assert ar.build_subject(0, 500, 0).startswith("✅")


def test_cuerpo_incluye_recursos():
    body = ar.build_html_body([], [], 10, None, "<h3>📊 Recursos de los contenedores</h3>")
    assert body.index("Prueba de vida") < body.index("📊 Recursos") < body.index("Un saludo")
