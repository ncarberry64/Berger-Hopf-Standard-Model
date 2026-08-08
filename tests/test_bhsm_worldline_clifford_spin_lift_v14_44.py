from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.completion.worldline_clifford_spin_lift_v14_44 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    commutant_complex_dimension,
    completion_payload,
    dirac_gamma_matrices,
    full_clifford_matcher_payload,
    materialize,
    normal_symbol,
    product_superconnection_payload,
    spinor_branch_connectivity_payload,
    worldline_action_ownership_payload,
    worldline_square_witness,
)


def test_worldline_square_witness() -> None:
    payload = worldline_square_witness()
    assert payload["validation_passed"]
    assert payload["residual"] < 1.0e-13


def test_current_action_does_not_promote_worldline_susy() -> None:
    payload = worldline_action_ownership_payload()
    assert payload["validation_passed"]
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["minimal_moduli_SUSY_QM"]["action_status"].startswith("NEW_")


def test_product_superconnection_square() -> None:
    payload = product_superconnection_payload()
    assert payload["validation_passed"]
    assert payload["finite_witness"]["square_residual"] < 1.0e-13


def test_normal_only_matcher_has_large_commutant() -> None:
    assert commutant_complex_dimension([normal_symbol()]) == 8


def test_full_complex_clifford_commutant_is_scalar() -> None:
    assert commutant_complex_dimension(dirac_gamma_matrices()) == 1


def test_matcher_payload_reduces_to_common_phase() -> None:
    payload = full_clifford_matcher_payload()
    assert payload["validation_passed"]
    dims = payload["commutant_complex_dimensions"]
    assert dims == {"normal_symbol_only": 8, "full_complex_Clifford_module": 1}


def test_up_orbital_tensor_has_one_zero_spinor_branch() -> None:
    payload = spinor_branch_connectivity_payload()
    rows = payload["up"]["middle_light_L2"]
    zeros = [row for row in rows if not row["nonzero"]]
    assert len(zeros) == 1
    assert zeros[0]["total_source"] == "5/2"
    assert zeros[0]["total_target"] == "11/2"


def test_down_orbital_tensor_has_all_four_branches() -> None:
    payload = spinor_branch_connectivity_payload()
    assert all(row["nonzero"] for row in payload["down"]["middle_light_L2"])


def test_combined_branch_connectivity_is_twelve_of_sixteen() -> None:
    payload = spinor_branch_connectivity_payload()
    assert payload["combined_connected_branch_choices"] == 12
    assert payload["combined_total_branch_choices"] == 16
    assert payload["validation_passed"]


def test_completion_gate_fails_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["BHSM_complete"] is False
    assert payload["Mark_III"] == "NOT_REACHED"
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["physical_CKM_emitted"] is False
    assert payload["new_action_adopted"] is False


def test_materialization_is_deterministic(tmp_path: Path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())


def test_dirac_gamma_matrices_are_nonsingular() -> None:
    for gamma in dirac_gamma_matrices():
        assert gamma.shape == (4, 4)
        assert abs(np.linalg.det(gamma)) > 0.5
