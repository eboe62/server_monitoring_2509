"""Patrones de log_kern_batch (B10-2): emparejados por posición y sin código muerto.

Se lee el código sin importarlo (el ingestor necesita la BBDD y el entorno del contenedor).
"""
import ast
import pathlib
import re

KERN = pathlib.Path("src/log_ingestor/log_kern_batch.py")


def _lists():
    tree = ast.parse(KERN.read_text(encoding="utf-8"))
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in ("regex_patterns", "pattern_names"):
                    found[t.id] = [e.value for e in node.value.elts]
    return found["regex_patterns"], found["pattern_names"]


def test_same_length():
    patterns, names = _lists()
    assert len(patterns) == len(names)


def test_dead_patterns_removed():
    _, names = _lists()
    assert "10_trafic_blocked" not in names
    assert "15_port_scan" not in names


def test_each_pattern_matches_its_sample():
    patterns, names = _lists()
    samples = {
        "11_interface_multicast_promiscuous": "kernel: veth1a2b3c: entered promiscuous mode",
        "12_docker_interface_state_change": "kernel: br0: port 2(veth1a2b3c) entered forwarding state",
        "13_interface_rename": "kernel: eth0: renamed from veth1a2b3c",
        "14_interface_unregister": "kernel: veth1a2b3c (unregistering): left allmulticast mode",
    }
    for regex, name in zip(patterns, names):
        assert re.search(regex, samples[name]), name


def test_ufw_block_is_not_ingested():
    # Los bloqueos de UFW los cuenta la Línea B desde ufw.log
    patterns, _ = _lists()
    line = "kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:00:00:00:00:00 SRC=192.0.2.1 DST=192.0.2.2 PROTO=TCP SPT=1 DPT=23"
    assert not any(re.search(r, line) for r in patterns)
