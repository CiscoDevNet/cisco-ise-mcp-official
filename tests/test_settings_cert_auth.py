# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from clients.settings import ISESettings


def _base(**over):
    """Minimal valid kwargs for ISESettings; override per test.

    Fields use ``validation_alias`` and the model does NOT set
    ``populate_by_name``, so kwargs MUST be keyed by the env-var alias
    (e.g. ``ISE_IP``), not the Python field name.
    """
    kwargs = {"ISE_IP": "10.0.0.1"}
    kwargs.update(over)
    return kwargs


def _cert_files(tmp_path):
    cert = tmp_path / "client.pem"
    key = tmp_path / "client.key"
    cert.write_text("cert")
    key.write_text("key")
    return str(cert), str(key)


class TestCertAuthSettings:
    def test_defaults_verify_on_no_cert(self):
        s = ISESettings(**_base())
        assert s.ise_verify_server_cert is True
        assert s.ise_verify_hostname is True
        assert s.ise_client_cert is None
        assert s.client_cert_configured is False

    def test_cert_and_key_together_ok(self, tmp_path):
        cert, key = _cert_files(tmp_path)
        s = ISESettings(**_base(ISE_CLIENT_CERT=cert, ISE_CLIENT_KEY=key))
        assert s.client_cert_configured is True

    def test_cert_without_key_raises(self, tmp_path):
        cert, _ = _cert_files(tmp_path)
        with pytest.raises(ValidationError, match="ISE_CLIENT_KEY"):
            ISESettings(**_base(ISE_CLIENT_CERT=cert))

    def test_key_without_cert_raises(self, tmp_path):
        _, key = _cert_files(tmp_path)
        with pytest.raises(ValidationError, match="ISE_CLIENT_CERT"):
            ISESettings(**_base(ISE_CLIENT_KEY=key))

    def test_missing_cert_file_raises(self, tmp_path):
        _, key = _cert_files(tmp_path)
        with pytest.raises(ValidationError, match="does not exist"):
            ISESettings(**_base(
                ISE_CLIENT_CERT=str(tmp_path / "nope.pem"), ISE_CLIENT_KEY=key
            ))

    def test_missing_ca_bundle_raises(self):
        with pytest.raises(ValidationError, match="does not exist"):
            ISESettings(**_base(ISE_CA_BUNDLE="/no/such/ca.pem"))

    def test_hostname_true_with_verify_off_raises(self):
        with pytest.raises(ValidationError, match="ISE_VERIFY_HOSTNAME"):
            ISESettings(**_base(
                ISE_VERIFY_SERVER_CERT=False, ISE_VERIFY_HOSTNAME=True
            ))

    def test_hostname_false_with_verify_off_ok(self):
        s = ISESettings(**_base(
            ISE_VERIFY_SERVER_CERT=False, ISE_VERIFY_HOSTNAME=False
        ))
        assert s.ise_verify_server_cert is False
        assert s.ise_verify_hostname is False

    def test_empty_env_strings_treated_as_absent(self):
        s = ISESettings(**_base(ISE_CLIENT_CERT="", ISE_CLIENT_KEY=""))
        assert s.ise_client_cert is None
        assert s.client_cert_configured is False
