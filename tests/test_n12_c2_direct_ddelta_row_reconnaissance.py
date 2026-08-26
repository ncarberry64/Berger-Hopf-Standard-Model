import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")


def _payload() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_direct_delta_identity_and_one_row_reduction_are_fail_closed() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["direct_signed_Delta_recombination"] == "DERIVED"
    assert payload["adjudication"]["selected_line_b_psi_inverse_free_identity"] == "DERIVED"
    assert payload["adjudication"]["hard_response_evaluation"] == (
        "SPECTRAL_COMPLEMENT_NOT_BORDERED_SOLVE"
    )
    assert payload["adjudication"]["full_98_by_98_D2Delta_norm_required"] is False
    assert payload["adjudication"]["one_dominant_D2Delta_row_sufficient"] is True
    assert payload["adjudication"]["mixed_second_eigenline_vector_required"] is False
    assert payload["adjudication"]["mixed_second_eigenline_contraction"] == (
        "REDUCED_TO_ONE_HARD_ADJOINT_AND_LOCAL_SOURCE"
    )
    assert payload["adjudication"][
        "moving_eigenline_derivative_matrix_required_for_cb_row"
    ] is False
    assert payload["adjudication"]["complete_cb_row_assembly"] == (
        "FINITE_LOCAL_ACTION_SOURCE_JETS_AND_HARD_ADJOINTS_ONLY"
    )
    assert payload["adjudication"]["rigorous_dominant_row_enclosure_on_exact_tube"] == "OPEN"
    assert payload["adjudication"]["physical_event_stop_or_zero_force_found"] is False


def test_two_mesh_row_is_only_diagnostic() -> None:
    payload = _payload()
    diagnostic = payload["two_mesh_reconnaissance"]
    assert diagnostic["authority"] == "DIAGNOSTIC_ONLY_NOT_AN_INTERVAL_OR_ANALYTIC_BOUND"
    assert diagnostic["relative_mesh_discrepancy"] < 0.02
    assert diagnostic["fine_row_to_rigorous_ceiling_ratio"] < 1.0e-4
    replay = payload["reference_replay"]
    assert replay["stored_minus_inverse_free_b_psi"] > 0.0
    assert replay["certified_Delta_interval"][0] < replay["direct_Dlambda_N_Delta"]
    assert replay["direct_Dlambda_N_Delta"] < replay["certified_Delta_interval"][1]
    with np.load(DATA) as data:
        rows = np.asarray(data["direct_D2Delta_rows"], dtype=float)
        assert rows.shape == (2, 98)
        assert int(data["dominant_index"]) == 86


def test_second_eigenline_contraction_uses_small_hard_adjoint() -> None:
    reduction = _payload()["second_eigenline_adjoint_reduction"]
    assert reduction["authority"].startswith("EXACT_ANALYTIC_IDENTITY")
    assert reduction["defining_equation_residual_2_norm"] < 1.0e-14
    assert reduction["spectral_to_gap_only_ratio"] < 1.0e-3
    assert reduction["spectral_hard_adjoint_2_norm"] < 0.01
    with np.load(DATA) as data:
        assert data["third_variation_covector"].shape == (61,)
        assert data["third_variation_hard_adjoint"].shape == (61,)
        assert int(data["adjoint_selected_branch"]) == 24


def test_gate_and_downstream_claims_remain_open() -> None:
    claim = _payload()["claim_boundary"]
    assert claim["signed_D_Y_Delta"] == "OPEN_PENDING_RIGOROUS_ROW_REMAINDER"
    assert claim["actual_signed_duration_covector"] == "OPEN"
    assert claim["actual_projected_zero_source_force"] == "OPEN"
    assert claim["Gate8"] == "LOCKED"
    assert claim["chord_03_authorized"] is False
    assert claim["FULL_BHSM_COMPLETE"] is False
