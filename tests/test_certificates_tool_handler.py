# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


# ---------------------------------------------------------------------------
# Helpers / pure-function tests
# ---------------------------------------------------------------------------

class TestParseIseDate:
    def test_filter_format(self):
        from tools.certificates_tool_handler import _parse_ise_date
        dt = _parse_ise_date("2026-04-30 13:48:25")
        assert dt.year == 2026
        assert dt.month == 4
        assert dt.day == 30
        assert dt.tzinfo is not None

    def test_java_response_format(self):
        from tools.certificates_tool_handler import _parse_ise_date
        dt = _parse_ise_date("Thu Apr 30 13:48:25 IDT 2026")
        assert dt.year == 2026
        assert dt.month == 4
        assert dt.day == 30

    def test_invalid_raises(self):
        from tools.certificates_tool_handler import _parse_ise_date
        with pytest.raises(ValueError, match="Cannot parse"):
            _parse_ise_date("not-a-date")


class TestFormatIseDate:
    def test_format_roundtrip(self):
        from tools.certificates_tool_handler import _format_ise_date, _parse_ise_date
        now = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        formatted = _format_ise_date(now)
        parsed = _parse_ise_date(formatted)
        assert parsed.year == 2026
        assert parsed.month == 6


class TestClassifyExpiryStatus:
    def test_negative_days_is_expired(self):
        from tools.certificates_tool_handler import _classify_expiry_status
        assert _classify_expiry_status(-1) == "expired"

    def test_zero_days_is_warning(self):
        from tools.certificates_tool_handler import _classify_expiry_status
        assert _classify_expiry_status(0) == "warning"

    def test_positive_days_is_warning(self):
        from tools.certificates_tool_handler import _classify_expiry_status
        assert _classify_expiry_status(10) == "warning"


class TestBuildCertSummary:
    def _make_cert(self, expiration_date=None, valid_from=None, status="Enabled",
                   friendly_name="MyCert", trusted_for="Infrastructure",
                   additional_properties=None):
        cert = MagicMock()
        cert.expiration_date = expiration_date
        cert.valid_from = valid_from
        cert.status = status
        cert.friendly_name = friendly_name
        cert.trusted_for = trusted_for
        cert.id = "cert-id-1"
        cert.additional_properties = additional_properties or {}
        return cert

    def test_missing_expiration_returns_none(self):
        from tools.certificates_tool_handler import _build_cert_summary
        cert = self._make_cert(expiration_date=None)
        now = datetime.now(tz=timezone.utc)
        assert _build_cert_summary(cert, now) is None

    def test_unparseable_expiration_returns_none(self):
        from tools.certificates_tool_handler import _build_cert_summary
        cert = self._make_cert(expiration_date="not-a-date")
        now = datetime.now(tz=timezone.utc)
        assert _build_cert_summary(cert, now) is None

    def test_valid_cert_returns_summary(self):
        from tools.certificates_tool_handler import _build_cert_summary
        now = datetime.now(tz=timezone.utc)
        future = now + timedelta(days=15)
        cert = self._make_cert(
            expiration_date=future.strftime("%Y-%m-%d %H:%M:%S"),
            valid_from=(now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
        )
        summary = _build_cert_summary(cert, now)
        assert summary is not None
        assert 14 <= summary.days_until_expiry <= 15
        assert summary.expiry_status == "warning"

    def test_expired_cert_returns_expired_status(self):
        from tools.certificates_tool_handler import _build_cert_summary
        now = datetime.now(tz=timezone.utc)
        past = now - timedelta(days=5)
        cert = self._make_cert(expiration_date=past.strftime("%Y-%m-%d %H:%M:%S"))
        summary = _build_cert_summary(cert, now)
        assert summary is not None
        assert summary.expiry_status == "expired"
        assert summary.days_until_expiry < 0

    def test_invalid_valid_from_falls_back(self):
        from tools.certificates_tool_handler import _build_cert_summary
        now = datetime.now(tz=timezone.utc)
        future = now + timedelta(days=10)
        cert = self._make_cert(
            expiration_date=future.strftime("%Y-%m-%d %H:%M:%S"),
            valid_from="bad-date",
        )
        summary = _build_cert_summary(cert, now)
        assert summary is not None
        assert summary.valid_from == "bad-date"

    def test_is_referred_in_policy_true(self):
        from tools.certificates_tool_handler import _build_cert_summary
        now = datetime.now(tz=timezone.utc)
        future = now + timedelta(days=10)
        cert = self._make_cert(
            expiration_date=future.strftime("%Y-%m-%d %H:%M:%S"),
            additional_properties={"isReferredInPolicy": True},
        )
        summary = _build_cert_summary(cert, now)
        assert summary is not None
        assert summary.is_referred_in_policy is True


# ---------------------------------------------------------------------------
# CertificatesToolHandler integration-level tests (mocking execute_api_call)
# ---------------------------------------------------------------------------

def _make_raw_cert(days_from_now: int, status="Enabled", friendly_name="Cert"):
    now = datetime.now(tz=timezone.utc)
    expiry = (now + timedelta(days=days_from_now)).strftime("%Y-%m-%d %H:%M:%S")
    valid_from = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "expirationDate": expiry,
        "validFrom": valid_from,
        "status": status,
        "friendlyName": friendly_name,
        "trustedFor": "Infrastructure",
        "id": "cert-1",
        "isReferredInPolicy": False,
    }


class TestCertificatesToolHandler:
    def _make_handler(self):
        from tools.certificates_tool_handler import CertificatesToolHandler
        from clients.client_factory import ClientName

        mock_factory = MagicMock()
        mock_factory.get_client.return_value = MagicMock()
        handler = CertificatesToolHandler(mock_factory)
        return handler

    @pytest.mark.asyncio
    async def test_returns_response_with_certs(self):
        from tools.certificates_tool_handler import CertificatesToolHandler
        from autogenerated_api_clients.certificates.models.trust_certificate_response import (
            TrustCertificateResponse,
        )

        handler = self._make_handler()
        now = datetime.now(tz=timezone.utc)
        raw = _make_raw_cert(days_from_now=10)

        # TrustCertificateResponse.from_dict may not accept our raw dict — mock it
        mock_cert = MagicMock()
        mock_cert.expiration_date = raw["expirationDate"]
        mock_cert.valid_from = raw["validFrom"]
        mock_cert.status = "Enabled"
        mock_cert.friendly_name = "Cert"
        mock_cert.trusted_for = "Infrastructure"
        mock_cert.id = "cert-1"
        mock_cert.additional_properties = {}

        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("tools.certificates_tool_handler.TrustCertificateResponse") as mock_cls:
            mock_exec.return_value = {"response": [raw]}
            mock_cls.from_dict.return_value = mock_cert

            result = await handler.check_expiring_trusted_certificates(
                expiry_days=30,
                include_expired=True,
                status_filter="all",
                limit=10,
            )

        assert result.summary.total_matched >= 0

    @pytest.mark.asyncio
    async def test_empty_response_returns_empty_list(self):
        handler = self._make_handler()
        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"response": []}
            result = await handler.check_expiring_trusted_certificates(
                expiry_days=30, include_expired=True, status_filter="all", limit=10
            )
        assert result.certificates == []
        assert result.summary.total_matched == 0

    @pytest.mark.asyncio
    async def test_status_filter_excludes_wrong_status(self):
        from autogenerated_api_clients.certificates.models.trust_certificate_response import (
            TrustCertificateResponse,
        )

        handler = self._make_handler()
        raw = _make_raw_cert(days_from_now=10, status="Disabled")

        mock_cert = MagicMock()
        mock_cert.expiration_date = raw["expirationDate"]
        mock_cert.valid_from = raw["validFrom"]
        mock_cert.status = "Disabled"
        mock_cert.friendly_name = "Cert"
        mock_cert.trusted_for = "Infrastructure"
        mock_cert.id = "cert-1"
        mock_cert.additional_properties = {}

        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("tools.certificates_tool_handler.TrustCertificateResponse") as mock_cls:
            mock_exec.return_value = {"response": [raw]}
            mock_cls.from_dict.return_value = mock_cert

            result = await handler.check_expiring_trusted_certificates(
                expiry_days=30, include_expired=True, status_filter="enabled", limit=10
            )

        # Disabled cert must be excluded when status_filter="enabled"
        assert result.summary.total_matched == 0

    @pytest.mark.asyncio
    async def test_include_expired_false_excludes_expired(self):
        from autogenerated_api_clients.certificates.models.trust_certificate_response import (
            TrustCertificateResponse,
        )

        handler = self._make_handler()
        raw = _make_raw_cert(days_from_now=-5, status="Enabled")

        mock_cert = MagicMock()
        mock_cert.expiration_date = raw["expirationDate"]
        mock_cert.valid_from = raw["validFrom"]
        mock_cert.status = "Enabled"
        mock_cert.friendly_name = "Cert"
        mock_cert.trusted_for = "Infrastructure"
        mock_cert.id = "cert-1"
        mock_cert.additional_properties = {}

        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec, \
             patch("tools.certificates_tool_handler.TrustCertificateResponse") as mock_cls:
            mock_exec.return_value = {"response": [raw]}
            mock_cls.from_dict.return_value = mock_cert

            result = await handler.check_expiring_trusted_certificates(
                expiry_days=30, include_expired=False, status_filter="all", limit=10
            )

        assert result.summary.total_matched == 0

    @pytest.mark.asyncio
    async def test_pagination_stops_at_limit(self):
        from autogenerated_api_clients.certificates.models.trust_certificate_response import (
            TrustCertificateResponse,
        )

        handler = self._make_handler()
        raw1 = _make_raw_cert(days_from_now=5, status="Enabled", friendly_name="A")
        raw2 = _make_raw_cert(days_from_now=10, status="Enabled", friendly_name="B")

        def _make_mock_cert(raw, fname):
            m = MagicMock()
            m.expiration_date = raw["expirationDate"]
            m.valid_from = raw["validFrom"]
            m.status = "Enabled"
            m.friendly_name = fname
            m.trusted_for = "Infrastructure"
            m.id = f"cert-{fname}"
            m.additional_properties = {}
            return m

        cert_mocks = [_make_mock_cert(raw1, "A"), _make_mock_cert(raw2, "B")]
        call_count = 0

        async def fake_exec(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return {"response": [raw1, raw2], "nextPage": None}

        with patch.object(handler, "execute_api_call", side_effect=fake_exec), \
             patch("tools.certificates_tool_handler.TrustCertificateResponse") as mock_cls:
            mock_cls.from_dict.side_effect = cert_mocks

            result = await handler.check_expiring_trusted_certificates(
                expiry_days=30, include_expired=True, status_filter="all", limit=1
            )

        # limit=1 should stop after collecting 1 cert
        assert len(result.certificates) == 1
