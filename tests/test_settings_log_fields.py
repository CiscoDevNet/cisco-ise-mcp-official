# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def test_log_fields_have_defaults(monkeypatch):
    monkeypatch.delenv("ISE_ADMIN_SESSION_COOKIE", raising=False)
    monkeypatch.delenv("LOG_CACHE_TTL_S", raising=False)
    monkeypatch.delenv("LOG_CACHE_DIR_PREFIX", raising=False)
    from clients.settings import ISESettings
    s = ISESettings(_env_file=None)
    assert s.ise_admin_session_cookie is None
    assert s.log_cache_ttl_s == 300.0
    assert s.log_cache_dir_prefix == "ise-logs-"


def test_empty_cookie_normalizes_to_none(monkeypatch):
    monkeypatch.setenv("ISE_ADMIN_SESSION_COOKIE", "")
    from clients.settings import ISESettings
    s = ISESettings(_env_file=None)
    assert s.ise_admin_session_cookie is None


def test_cookie_is_secret(monkeypatch):
    monkeypatch.setenv("ISE_ADMIN_SESSION_COOKIE", "APPSESSIONID=abc; MNTLA_JWT_TOKEN=xyz")
    from clients.settings import ISESettings
    s = ISESettings(_env_file=None)
    # SecretStr hides value in repr
    assert "APPSESSIONID" not in repr(s.ise_admin_session_cookie)
    assert s.ise_admin_session_cookie.get_secret_value().startswith("APPSESSIONID=")


def test_authlist_gate_defaults(monkeypatch):
    # Ensure a clean env so defaults apply.
    for var in (
        "ISE_AUTHLIST_MAX_CONCURRENCY",
        "ISE_AUTHLIST_MIN_INTERVAL_S",
        "ISE_AUTHLIST_BACKOFF_BASE_S",
        "ISE_AUTHLIST_BACKOFF_MAX_S",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ISE_IP", "192.0.2.1")

    from clients.settings import ISESettings

    s = ISESettings()
    assert s.authlist_max_concurrency == 1
    assert s.authlist_min_interval_s == 0.0
    assert s.authlist_backoff_base_s == 5.0
    assert s.authlist_backoff_max_s == 300.0


def test_authlist_empty_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("ISE_IP", "192.0.2.1")
    monkeypatch.setenv("ISE_AUTHLIST_MAX_CONCURRENCY", "")
    monkeypatch.setenv("ISE_AUTHLIST_MIN_INTERVAL_S", "")
    monkeypatch.setenv("ISE_AUTHLIST_BACKOFF_BASE_S", "")
    monkeypatch.setenv("ISE_AUTHLIST_BACKOFF_MAX_S", "")

    from clients.settings import ISESettings

    s = ISESettings()
    assert s.authlist_max_concurrency == 1
    assert s.authlist_min_interval_s == 0.0
    assert s.authlist_backoff_base_s == 5.0
    assert s.authlist_backoff_max_s == 300.0
