import os
import smtplib
from monitoring.common import config


class DummySMTP:
    def __init__(self, *a, **k):
        self.logged = None
        self.sent = False

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
    monkeypatch.setenv("SMTP_MODE", "relay")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)

    # avoid DNS resolution issues
    monkeypatch.setattr("socket.getaddrinfo", lambda *a, **k: [(None, None, None, None, ("127.0.0.1", 0))])

    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)
    config.init_config(secrets_required=False)
    ok = config.send_email("hello", "subj")
    assert ok is True


def test_send_auth_login(monkeypatch):
    monkeypatch.setenv("SMTP_MODE", "auth")
    monkeypatch.setenv("SMTP_USER", "u123")
    monkeypatch.setenv("SMTP_PASS", "p123")

    monkeypatch.setattr("socket.getaddrinfo", lambda *a, **k: [(None, None, None, None, ("127.0.0.1", 0))])
    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)

    config.init_config(secrets_required=True)
    ok = config.send_email("hello", "subj")
    assert ok is True
