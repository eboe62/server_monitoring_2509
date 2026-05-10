import os
import pytest
from monitoring.common import config


def test_relay_mode_no_secrets(monkeypatch):
    monkeypatch.setenv("SMTP_MODE", "relay")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    # Should not raise and should return config with None creds
    cfg = config.init_config()
    assert cfg["SMTP_USER"] is None and cfg["SMTP_PASS"] is None


def test_auth_mode_with_files(tmp_path, monkeypatch):
    monkeypatch.setenv("SMTP_MODE", "auth")
    sdir = tmp_path / "secrets"
    sdir.mkdir()
    (sdir / "smtp_user").write_text("user123")
    (sdir / "smtp_pass").write_text("pass123")
    cfg = config.init_config(secrets_dir=str(sdir))
    assert cfg["SMTP_USER"] == "user123"
    assert cfg["SMTP_PASS"] == "pass123"


def test_auth_mode_missing_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("SMTP_MODE", "auth")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    # use an empty tmp secrets dir to avoid existing workspace secrets
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    with pytest.raises(RuntimeError):
        config.init_config(secrets_dir=str(secrets_dir))
