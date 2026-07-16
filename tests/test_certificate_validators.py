# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastmcp.exceptions import ToolError


class TestValidateExpiryDays:
    def test_valid_value_returned_unchanged(self):
        from utils.certificate_validators import validate_expiry_days
        assert validate_expiry_days(30) == 30

    def test_min_boundary_accepted(self):
        from utils.certificate_validators import validate_expiry_days
        assert validate_expiry_days(1) == 1

    def test_max_boundary_accepted(self):
        from utils.certificate_validators import validate_expiry_days
        assert validate_expiry_days(365) == 365

    def test_zero_raises(self):
        from utils.certificate_validators import validate_expiry_days
        with pytest.raises(ToolError):
            validate_expiry_days(0)

    def test_negative_raises(self):
        from utils.certificate_validators import validate_expiry_days
        with pytest.raises(ToolError):
            validate_expiry_days(-1)

    def test_over_max_raises(self):
        from utils.certificate_validators import validate_expiry_days
        with pytest.raises(ToolError):
            validate_expiry_days(366)


class TestValidateCertLimit:
    def test_valid_limit_returned(self):
        from utils.certificate_validators import validate_cert_limit
        assert validate_cert_limit(10) == 10

    def test_max_limit_accepted(self):
        from utils.certificate_validators import validate_cert_limit
        assert validate_cert_limit(100) == 100

    def test_over_max_raises(self):
        from utils.certificate_validators import validate_cert_limit
        with pytest.raises(ToolError):
            validate_cert_limit(101)

    def test_zero_raises(self):
        from utils.certificate_validators import validate_cert_limit
        with pytest.raises(ToolError):
            validate_cert_limit(0)


class TestValidateCertStatusFilter:
    def test_all_accepted(self):
        from utils.certificate_validators import validate_cert_status_filter
        assert validate_cert_status_filter("all") == "all"

    def test_enabled_accepted(self):
        from utils.certificate_validators import validate_cert_status_filter
        assert validate_cert_status_filter("enabled") == "enabled"

    def test_disabled_accepted(self):
        from utils.certificate_validators import validate_cert_status_filter
        assert validate_cert_status_filter("disabled") == "disabled"

    def test_case_insensitive(self):
        from utils.certificate_validators import validate_cert_status_filter
        assert validate_cert_status_filter("ENABLED") == "enabled"

    def test_whitespace_stripped(self):
        from utils.certificate_validators import validate_cert_status_filter
        assert validate_cert_status_filter("  all  ") == "all"

    def test_invalid_raises(self):
        from utils.certificate_validators import validate_cert_status_filter
        with pytest.raises(ToolError):
            validate_cert_status_filter("unknown")
