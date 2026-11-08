"""alert_risk (B4): clasificación con ADMIN_IPS y asunto del correo. Sin BBDD ni SMTP."""
from log_ingestor import alert_risk as ar


def _row(ip):
    # Misma forma que RISK_QUERY: la IP en la posición IP_COLUMN
    row = [None] * len(ar.HEADERS)
    row[ar.IP_COLUMN] = ip
    return tuple(row)


def test_parse_admin_ips_ignora_vacios_y_espacios():
    assert ar.parse_admin_ips(" 203.0.113.7 , ,198.51.100. ") == ["203.0.113.7", "198.51.100."]
    assert ar.parse_admin_ips(None) == []
    assert ar.parse_admin_ips("") == []


def test_is_admin_ip_tres_formas():
    rules = ["203.0.113.7", "198.51.100.", "192.0.2.0/24"]
    assert ar.is_admin_ip("203.0.113.7", rules)        # exacta
    assert not ar.is_admin_ip("203.0.113.70", rules)   # exacta no es prefijo
    assert ar.is_admin_ip("198.51.100.23", rules)      # prefijo
    assert ar.is_admin_ip("192.0.2.200", rules)        # CIDR
    assert not ar.is_admin_ip("192.0.3.1", rules)
    assert not ar.is_admin_ip(None, rules)
    assert not ar.is_admin_ip("no-es-ip", ["10.0.0.0/8"])


def test_classify_rows_separa_sin_ocultar():
    rows = [_row("203.0.113.7"), _row("45.0.0.1"), _row("198.51.100.9")]
    threats, admins = ar.classify_rows(rows, ["203.0.113.7", "198.51.100."])
    assert [r[ar.IP_COLUMN] for r in threats] == ["45.0.0.1"]
    assert len(admins) == 2
    assert len(threats) + len(admins) == len(rows)


def test_sin_admin_ips_todo_es_amenaza():
    threats, admins = ar.classify_rows([_row("203.0.113.7")], [])
    assert len(threats) == 1 and admins == []


def test_build_subject_tres_casos():
    assert ar.build_subject(0, 0).startswith("⚠️")
    assert ar.build_subject(3, 0).startswith("⚠️")   # sin datos manda sobre todo
    assert ar.build_subject(2, 500) == "🚨 Alerta: 2 amenazas de alto riesgo"
    assert ar.build_subject(0, 500).startswith("✅")


def test_build_html_body_bloques():
    body = ar.build_html_body([_row("45.0.0.1")], [_row("203.0.113.7")], 42, None)
    assert "🚨 Amenazas" in body and "✅ Prueba de vida" in body
    assert body.index("45.0.0.1") < body.index("203.0.113.7")
    assert "<strong>42</strong>" in body
    vacio = ar.build_html_body([], [], 0, None)
    assert "Sin amenazas" in vacio and "No ha entrado ningún registro" in vacio
