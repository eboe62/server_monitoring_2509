import os
import importlib
import pytest

from monitoring.common import config

def test_invalid_smtp_mode(monkeypatch):
    monkeypatch.setenv("SMTP_MODE", "invalid_mode")
    with pytest.raises(RuntimeError):
        config.get_smtp_mode()

    # Clear env and set valid
    monkeypatch.setenv("SMTP_MODE", "relay")
    assert config.get_smtp_mode() == "relay"
