# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from clients.url_safety import assert_url_under_base, validate_endpoint


class TestValidateEndpoint:
    def test_valid_endpoint_returned_unchanged(self):
        assert validate_endpoint("Session/ActiveList") == "Session/ActiveList"

    def test_valid_simple_path(self):
        assert validate_endpoint("foo") == "foo"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="non-empty string"):
            validate_endpoint("")

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="non-empty string"):
            validate_endpoint(None)  # type: ignore[arg-type]

    def test_leading_slash_raises(self):
        with pytest.raises(ValueError, match="must not start with '/'"):
            validate_endpoint("/Session/ActiveList")

    def test_scheme_injection_raises(self):
        with pytest.raises(ValueError, match="forbidden sequence"):
            validate_endpoint("http://evil.com")

    def test_path_traversal_raises(self):
        with pytest.raises(ValueError, match="forbidden sequence"):
            validate_endpoint("foo/../etc/passwd")

    def test_backslash_raises(self):
        with pytest.raises(ValueError, match="forbidden sequence"):
            validate_endpoint("foo\\bar")

    def test_carriage_return_raises(self):
        with pytest.raises(ValueError, match="forbidden sequence"):
            validate_endpoint("foo\rbar")

    def test_newline_raises(self):
        with pytest.raises(ValueError, match="forbidden sequence"):
            validate_endpoint("foo\nbar")


class TestAssertUrlUnderBase:
    def test_url_under_base_passes(self):
        assert_url_under_base(
            "https://host/admin/API/mnt/Session/ActiveList",
            "https://host/admin/API/mnt/",
        )

    def test_url_not_under_base_raises(self):
        with pytest.raises(ValueError, match="escaped base_url"):
            assert_url_under_base(
                "https://evil.com/admin/API/mnt/Session",
                "https://host/admin/API/mnt/",
            )
