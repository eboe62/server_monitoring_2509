import os
import shutil
from monitoring.common import config


def test_init_config_modes_ci(tmp_path):
    # Relay mode: should not raise
    os.environ.pop("SMTP_USER", None)
    os.environ.pop("SMTP_PASS", None)
    os.environ["SMTP_MODE"] = "relay"
    cfg = config.init_config(secrets_required=None)
    assert cfg["SMTP_USER"] is None

    # Auth mode missing secrets: must raise
    os.environ["SMTP_MODE"] = "auth"
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    user = secrets_dir / "smtp_user"
    pw = secrets_dir / "smtp_pass"
    # ensure absent
    if user.exists():
        user.unlink()
    if pw.exists():
        pw.unlink()

    try:
        try:
            config.init_config(secrets_dir=str(secrets_dir), secrets_required=None)
            raise AssertionError("Expected RuntimeError for missing auth secrets")
        except RuntimeError:
            pass
    finally:
        os.environ.pop("SMTP_MODE", None)
