import smtplib
from monitoring.common import config


class DummySMTP:

    last_instance = None

    def __init__(self, *a, **k):
        self.logged = None
        self.sent = False

        DummySMTP.last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def has_extn(self, e):
        return False

    def ehlo(self):
        return (250, b"OK")

    def starttls(self):
        return (220, b"Ready to start TLS")

    def login(self, u, p):
        self.logged = (u, p)
        return (235, b"2.7.0 Authentication successful")

    def sendmail(self, f, r, m):
        self.sent = True
        return {}


def test_send_relay_no_login(monkeypatch):
    """
    relay:
      - no requiere auth
      - no debe ejecutar login()
    """

    # limpiar estado previo global
    DummySMTP.last_instance = None

    monkeypatch.setenv("SMTP_MODE", "relay")

    # IMPORTANTE:
    # limpiar variables para evitar contaminación CI/CD
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    monkeypatch.setenv("EMAIL_FROM", "noreply@test.local")

    # evitar lectura accidental de secrets reales
    monkeypatch.setenv(
        "SMTP_RELAY_SECRETS_DIR",
        "/tmp/nonexistent-secrets"
    )

    # evitar resolución DNS real
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [
            (None, None, None, None, ("127.0.0.1", 0))
        ],
    )

    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)
    config.init_config()
    ok = config.send_email(
        html_content="hello",
        subject="subj",
        email_to="test@example.com",
    )

    assert ok is True

    smtp_instance = DummySMTP.last_instance

    assert smtp_instance is not None
    assert smtp_instance.sent is True

    # relay NO debe autenticarse
    assert smtp_instance.logged is None

def test_send_auth_login(monkeypatch, tmp_path):
    """
    auth:
      - requiere auth SMTP
      - debe ejecutar login()
    """

    # limpiar estado previo global
    DummySMTP.last_instance = None

    monkeypatch.setenv("SMTP_MODE", "auth")
    monkeypatch.setenv("EMAIL_FROM", "noreply@test.local")

    # NO usar variables entorno para evitar contaminación
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)

    # crear secrets temporales controlados
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()

    (secrets_dir / "smtp_user").write_text("u123")
    (secrets_dir / "smtp_pass").write_text("p123")

    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [
            (None, None, None, None, ("127.0.0.1", 0))
        ],
    )

    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)

    config.init_config(secrets_dir=str(secrets_dir))
    ok = config.send_email(
        html_content="hello",
        subject="subj",
        email_to="test@example.com",
    )

    assert ok is True

    smtp_instance = DummySMTP.last_instance

    assert smtp_instance is not None
    assert smtp_instance.sent is True

    # auth SÍ debe autenticarse
    assert smtp_instance.logged == ("u123", "p123")


def _fake_dns(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [(None, None, None, None, ("127.0.0.1", 0))],
    )


def test_relay_logs_no_enganosos(monkeypatch, capsys, tmp_path):
    """B7: en relay sin credenciales no se escribe 'Autenticando' ni el aviso de .env
    cuando las variables del correo ya llegan por el entorno (caso de los contenedores)."""
    monkeypatch.setenv("SMTP_MODE", "relay")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    monkeypatch.setenv("EMAIL_FROM", "noreply@test.local")
    monkeypatch.setenv("EMAIL_TO", "dest@test.local")
    _fake_dns(monkeypatch)
    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)

    config.init_config(env_path=str(tmp_path / "no-existe.env"),
                       secrets_dir=str(tmp_path / "no-secrets"))
    assert config.send_email(html_content="hola", subject="s", email_to="t@example.com")

    out = capsys.readouterr().out
    assert ".env no encontrado" not in out
    assert "Autenticando" not in out
    assert "Modo relay: envío sin autenticación" in out


def test_aviso_env_si_faltan_variables(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("SMTP_MODE", "relay")
    monkeypatch.delenv("EMAIL_FROM", raising=False)
    monkeypatch.delenv("EMAIL_TO", raising=False)
    config.init_config(env_path=str(tmp_path / "no-existe.env"),
                       secrets_dir=str(tmp_path / "no-secrets"))
    assert "faltan EMAIL_FROM/EMAIL_TO" in capsys.readouterr().out
