from __future__ import annotations

from pathlib import Path

import sympy as sp

from bhsm.interface.completion.foundational_dirac_spin_glue_v14_45 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    RENORMALIZATION_VERDICT,
    collective_projector_witness,
    completion_payload,
    counterterm_matrix,
    counterterm_solution,
    counterterm_underdetermination_payload,
    foundational_action_payload,
    global_spin_glue_payload,
    materialize,
    no_double_counting_payload,
    spin_seam_cancellation_witness,
    zero_mode_pullback_payload,
)


def test_foundational_action_is_adopted_but_not_misreported_as_derived() -> None:
    payload = foundational_action_payload()
    assert payload["validation_passed"]
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["status"] == "FOUNDATIONAL_EFFECTIVE_ACTION_ADOPTED"
    assert payload["not_status"] == "DERIVED_FROM_THE_BOSONIC_PATH_B_ACTION"


def test_eta_zero_mode_pullback_is_exactly_canonical() -> None:
    payload = zero_mode_pullback_payload()
    assert payload["validation_passed"]
    witness = payload["numerical_witness"]
    assert abs(witness["weighted_norm"] - 1.0) < 1.0e-12
    assert abs(witness["two_sheet_overlap"] - 1.0) < 1.0e-12
    assert witness["max_first_order_residual"] < 1.0e-13


def test_internal_seam_Green_forms_cancel() -> None:
    witness = spin_seam_cancellation_witness()
    assert witness["validation_passed"]
    assert witness["cancellation_residual"] < 1.0e-13


def test_global_spin_bundle_fixes_matcher_without_flavor_holonomy() -> None:
    payload = global_spin_glue_payload()
    assert payload["validation_passed"]
    assert payload["matcher_status"] == "FIXED_BY_THE_ADOPTED_GLOBAL_SPIN_BUNDLE"
    assert payload["validation"]["spin_glue_does_not_generate_CKM"]


def test_collective_projector_is_orthogonal() -> None:
    witness = collective_projector_witness()
    assert witness["validation_passed"]
    assert witness["rank_P"] == witness["collective_dimension"] == 3


def test_no_double_counting_contract() -> None:
    payload = no_double_counting_payload()
    assert payload["validation_passed"]
    assert "det-prime" in payload["measure_contract"]["bosonic_one_loop_sector"]


def test_counterterm_channel_matrix_is_full_rank() -> None:
    matrix = counterterm_matrix()
    assert matrix.det() == 420
    assert matrix.rank() == 2


def test_counterterm_solution_reconstructs_arbitrary_targets() -> None:
    pi2 = sp.Rational(4, 11)
    pi3 = -sp.Rational(7, 19)
    target2 = sp.Rational(-2, 3)
    target3 = sp.Rational(5, 7)
    c2, c4 = counterterm_solution(target2, target3, pi2, pi3)
    reconstructed = counterterm_matrix() * sp.Matrix([c2, c4]) + sp.Matrix(
        [pi2, pi3]
    )
    assert reconstructed == sp.Matrix([target2, target3])


def test_counterterm_payload_fails_the_physical_crossing_closed() -> None:
    payload = counterterm_underdetermination_payload()
    assert payload["validation_passed"]
    assert payload["renormalization_verdict"] == RENORMALIZATION_VERDICT
    assert payload["determinant"] == 420


def test_completion_gate_records_foundational_progress_without_completion() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["BHSM_complete"] is False
    assert payload["Mark_III"] == "NOT_REACHED"
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["scientific_result"]["fermion_action_derived_from_Path_B"] is False
    assert payload["scientific_result"]["renormalized_bifurcation_status"] == "UNDERDETERMINED"


def test_materialization_is_deterministic(tmp_path: Path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())


def test_no_physical_outputs_are_emitted() -> None:
    payload = completion_payload()
    validation = payload["validation"]
    assert validation["physical_Pi2_not_emitted"]
    assert validation["physical_Pi3_not_emitted"]
    assert validation["physical_CKM_not_emitted"]
    assert validation["physical_CP_not_emitted"]
    assert validation["physical_mass_not_emitted"]
    assert validation["physical_scale_not_emitted"]
