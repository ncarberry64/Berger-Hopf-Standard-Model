from __future__ import annotations

import pytest

from bhsm.interface.completion.source_free_relative_frame_v14_41 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    classical_relative_frame_payload,
    coexact_shift_eigenvalue,
    coexact_shift_multiplicity,
    collective_fermion_quantum_gate_payload,
    completion_payload,
    hodge_coexact_one_form_eigenvalue,
    materialize,
    normalized_quadratic_coefficient,
    round_cap_spectrum_payload,
    vacuum_polarization_threshold,
)


def test_round_s3_shift_spectrum_exact() -> None:
    assert hodge_coexact_one_form_eigenvalue(1) == 4.0
    assert coexact_shift_eigenvalue(1) == 0.0
    assert coexact_shift_eigenvalue(2) == 5.0
    assert coexact_shift_eigenvalue(3) == 12.0


def test_non_killing_spectrum_is_positive() -> None:
    assert all(coexact_shift_eigenvalue(L) > 0.0 for L in range(2, 12))


def test_killing_multiplicity_and_scaling() -> None:
    assert coexact_shift_multiplicity(1) == 6
    assert coexact_shift_eigenvalue(2, radius=2.0) == pytest.approx(1.25)
    assert normalized_quadratic_coefficient(
        2, radius=2.0, lapse=2.0, gravity_coefficient=4.0
    ) == pytest.approx(0.625)


def test_invalid_geometric_parameters_fail_closed() -> None:
    with pytest.raises(ValueError):
        coexact_shift_eigenvalue(0)
    with pytest.raises(ValueError):
        coexact_shift_eigenvalue(2, radius=0.0)
    with pytest.raises(ValueError):
        normalized_quadratic_coefficient(2, lapse=0.0)


def test_classical_source_free_relative_frame_is_off() -> None:
    payload = classical_relative_frame_payload()
    assert payload["validation_passed"]
    assert payload["classical_gate"]["spontaneous_source_free_relative_frame"] is False
    assert payload["classical_gate"]["L2"] == "OFF_STRICTLY_POSITIVE"
    assert payload["classical_gate"]["L3"] == "OFF_STRICTLY_POSITIVE"


def test_quantum_zero_crossing_threshold_contract() -> None:
    assert vacuum_polarization_threshold(2) == -5.0
    assert vacuum_polarization_threshold(3) == -12.0
    payload = collective_fermion_quantum_gate_payload()
    assert payload["validation_passed"]
    assert payload["status"] == "OPEN_NOT_NUMERICALLY_EVALUABLE"


def test_round_cap_payload_records_requested_channels() -> None:
    payload = round_cap_spectrum_payload()
    assert payload["validation_passed"]
    assert payload["flavor_channels"]["L2"]["eigenvalue"] == "5/R^2"
    assert payload["flavor_channels"]["L3"]["eigenvalue"] == "12/R^2"


def test_completion_gate_fails_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["classical_result"]["spontaneous_classical_relative_frame"] is False
    assert payload["quantum_result"]["zero_crossing_evaluated"] is False
    assert payload["validation"]["BHSM_not_complete"]


def test_materialization_is_deterministic(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
