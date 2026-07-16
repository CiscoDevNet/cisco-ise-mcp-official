# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from clients.request_context import (
    get_per_user_credential,
    has_per_user_credential,
    reset_per_user_credential,
    set_per_user_credential,
)


class TestRequestContext:
    def test_default_is_none(self):
        token = set_per_user_credential(None)
        try:
            assert get_per_user_credential() is None
        finally:
            reset_per_user_credential(token)

    def test_set_and_get(self):
        token = set_per_user_credential("Basic dXNlcjpwYXNz")
        try:
            assert get_per_user_credential() == "Basic dXNlcjpwYXNz"
        finally:
            reset_per_user_credential(token)

    def test_reset_restores_prior_value(self):
        outer = set_per_user_credential("Basic outer")
        try:
            inner = set_per_user_credential("Basic inner")
            assert get_per_user_credential() == "Basic inner"
            reset_per_user_credential(inner)
            assert get_per_user_credential() == "Basic outer"
        finally:
            reset_per_user_credential(outer)

    def test_has_credential_false_when_none(self):
        token = set_per_user_credential(None)
        try:
            assert has_per_user_credential() is False
        finally:
            reset_per_user_credential(token)

    def test_has_credential_true_when_set(self):
        token = set_per_user_credential("Basic dXNlcjpwYXNz")
        try:
            assert has_per_user_credential() is True
        finally:
            reset_per_user_credential(token)
