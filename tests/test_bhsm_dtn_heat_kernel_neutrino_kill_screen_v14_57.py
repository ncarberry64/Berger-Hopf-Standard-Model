from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.completion.dtn_heat_kernel_neutrino_kill_screen_v14_57 import (
    EXACT_NEXT_OBJECT,
    artifact_payloads,
    completion_gate_payload,
    current_archive_readiness_payload,
    diagnostic_bundle,
    diagnostic_pipeline_payload,
    effective_wake_generator,
    independent_relative_gaps,
    materialize,
    matrix_from_json,
    matrix_to_json,
    no_retuning_kill_screen_contract_payload,
    positive_spectrum,
    primed_logdet_difference,
    projected_dtn_matching_operator,
    relative_heat_trace,
    relative_zeta_prime_zero,
    relative_zeta_zero,
    unitary_from_hermitian,
    unitarity_residual,
    validate_bundle,
    validate_projector,
)


def _m(bundle: dict, name: str) -> np.ndarray:
    return matrix_from_json(bundle["matrices"][name])


def test_complex_matrix_json_round_trip() -> None:
    matrix = np.array([[1, 1j, 0], [-1j, 2, 0.5], [0, 0.5, 3]], dtype=complex)
    assert np.allclose(matrix_from_json(matrix_to_json(matrix)), matrix)


def test_diagnostic_bundle_is_structurally_valid_but_not_physical() -> None:
    bundle = diagnostic_bundle()
    assert validate_bundle(bundle, physical=False)["valid"] is True
    physical = validate_bundle(bundle, physical=True)
    assert physical["valid"] is False
    assert "physical execution requires mode=physical" in physical["errors"]


def test_projector_validation() -> None:
    validate_projector(np.eye(3, dtype=complex))
    with pytest.raises(ValueError):
        validate_projector(np.diag([1.0, 0.5, 0.0]).astype(complex))


def test_identical_dtn_maps_have_zero_matching_operator() -> None:
    matrix = np.diag([1.0, 2.0, 3.0]).astype(complex)
    result = projected_dtn_matching_operator(matrix, matrix, np.zeros((3, 3)), np.eye(3))
    assert np.linalg.norm(result) < 1e-14


def test_diagnostic_dtn_contrast_is_nonzero_and_hermitian() -> None:
    bundle = diagnostic_bundle()
    result = projected_dtn_matching_operator(
        _m(bundle, "child_dtn"),
        _m(bundle, "parent_dtn"),
        _m(bundle, "interface_hessian"),
        _m(bundle, "physical_projector"),
    )
    assert np.linalg.norm(result) > 0.1
    assert np.linalg.norm(result - result.conj().T) < 1e-14


def test_relative_heat_trace_is_finite() -> None:
    bundle = diagnostic_bundle()
    value = relative_heat_trace(
        _m(bundle, "child_heat_operator"),
        _m(bundle, "parent_heat_operator"),
        0.3,
    )
    assert np.isfinite(value)


def test_relative_zeta_zero_equals_primed_rank_difference() -> None:
    child = np.diag([1.0, 2.0, 0.0]).astype(complex)
    parent = np.diag([3.0, 0.0, 0.0]).astype(complex)
    assert relative_zeta_zero(child, parent) == pytest.approx(1.0)


def test_zeta_prime_logdet_identity() -> None:
    bundle = diagnostic_bundle()
    child = _m(bundle, "child_heat_operator")
    parent = _m(bundle, "parent_heat_operator")
    assert relative_zeta_prime_zero(child, parent) == pytest.approx(
        -primed_logdet_difference(child, parent), abs=1e-13
    )


def test_positive_spectrum_rejects_negative_mode() -> None:
    with pytest.raises(ValueError):
        positive_spectrum(np.diag([1.0, -0.01, 2.0]).astype(complex))


def test_effective_generator_is_traceless_hermitian() -> None:
    generator = effective_wake_generator(diagnostic_bundle())
    assert np.linalg.norm(generator - generator.conj().T) < 1e-14
    assert abs(np.trace(generator)) < 1e-13


def test_generator_has_two_nonzero_independent_gaps() -> None:
    bundle = diagnostic_bundle()
    generator = effective_wake_generator(bundle)
    gaps = independent_relative_gaps(generator, bundle["coefficients"]["cycle_period"])
    assert abs(gaps[0]) > 1e-6
    assert abs(gaps[1] - gaps[0]) > 1e-6


def test_monodromy_is_unitary() -> None:
    bundle = diagnostic_bundle()
    generator = effective_wake_generator(bundle)
    unitary = unitary_from_hermitian(generator, bundle["coefficients"]["cycle_period"])
    assert unitarity_residual(unitary) < 1e-12


def test_diagnostic_pipeline_preserves_pair_and_changes_matter_response() -> None:
    payload = diagnostic_pipeline_payload()
    assert payload["pair_identity_changed"] is False
    assert payload["free_kick_commutator_norm"] > 1e-6
    assert payload["vacuum_detector_probabilities"] != payload["matter_detector_probabilities"]
    assert sum(payload["vacuum_detector_probabilities"]) == pytest.approx(1.0)
    assert sum(payload["matter_detector_probabilities"]) == pytest.approx(1.0)
    assert payload["moving_seam_bvp_insertion"]["combined_residual_norm"] < 1e-12


def test_kill_screen_forbids_retuning() -> None:
    payload = no_retuning_kill_screen_contract_payload()
    assert "post-comparison retuning allowed" in payload["hard_fail_conditions"]
    assert payload["physical_target_values_bundled"] is False


def test_current_archive_is_fail_closed() -> None:
    payload = current_archive_readiness_payload()
    assert payload["diagnostic_pipeline_valid"] is True
    assert payload["physical_pipeline_valid"] is False
    assert payload["physical_result_emitted"] is False
    assert len(payload["missing_proof_flags"]) >= 10


def test_completion_gate_remains_open() -> None:
    gate = completion_gate_payload()
    assert gate["full_BHSM_complete"] is False
    assert gate["mark_III"] == "NOT_REACHED"
    assert gate["physical_neutrino_prediction_emitted"] is False
    assert gate["usb_touched"] is False
    assert gate["exact_next_object"] == EXACT_NEXT_OBJECT


def test_artifact_materialization_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    paths_first = materialize(first)
    paths_second = materialize(second)
    assert len(paths_first) == len(artifact_payloads()) == 7
    for path_a, path_b in zip(paths_first, paths_second):
        assert path_a.name == path_b.name
        assert path_a.read_bytes() == path_b.read_bytes()
        json.loads(path_a.read_text(encoding="utf-8"))
