# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from utils.sampling import build_sampling_note


def test_empty_returns_no_note():
    note = build_sampling_note(sample_size=0, total_found=0, resource="session")
    assert note is None


def test_complete_when_sample_equals_total_returns_no_note():
    note = build_sampling_note(sample_size=3, total_found=3, resource="session")
    assert note is None


def test_complete_when_sample_exceeds_total_returns_no_note():
    """Defensive: sample > total should not produce nonsense; no note emitted."""
    note = build_sampling_note(sample_size=5, total_found=3, resource="session")
    assert note is None


def test_sample_states_n_of_m():
    note = build_sampling_note(sample_size=1, total_found=2, resource="session")
    assert "sample" in note.lower()
    assert "1 out of 2" in note


def test_sample_does_not_reference_field_name():
    """The note must not hardcode a list field name like 'sample_sessions',
    so future tools are free to name their list field however they like."""
    note = build_sampling_note(sample_size=1, total_found=2, resource="session")
    assert "sample_sessions" not in note


def test_resource_noun_is_used():
    note = build_sampling_note(sample_size=1, total_found=2, resource="certificate")
    assert "certificates" in note


def test_default_resource_noun():
    note = build_sampling_note(sample_size=1, total_found=2)
    assert "results" in note
