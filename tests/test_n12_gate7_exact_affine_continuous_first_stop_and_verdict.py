from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
BRACKET = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_SELECTED_EIGENVALUE_BRACKET.json"
STOP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
STOP_DATA = STOP.with_suffix(".npz")
VERDICT = BASE / "BHSM_N12_GATE7_FINAL_EXACT_CENTER_FORCE_KKT_HESSIAN_VERDICT.json"
TRANSVERSALITY = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_STOP_TRANSVERSALITY.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_terminal_action_owned_selected_eigenvalue_bracket_is_strict() -> None:
    record = _load(BRACKET)
    assert record["validation_passed"] is True
    terminal = record["terminal_cell"]
    assert terminal["left"]["selected_branch"] == 24
    assert terminal["right"]["selected_branch"] == 24
    assert terminal["left"]["selected_eigenvalue_interval"][0] > 0.0
    assert terminal["right"]["selected_eigenvalue_interval"][1] < 0.0
    assert terminal["left"]["causal_solution_halo_radius"] == 5.798470127958652e-13
    assert terminal["right"]["causal_solution_halo_radius"] == 5.798470127958652e-13
    assert record["stop_equation"] == "lambda_24=0"


def test_continuous_cover_certifies_canonical_earliest_stop() -> None:
    record = _load(STOP)
    assert record["validation_passed"] is True
    assert record["birth_cell"]["minimum_exact_Bernstein_lower"] > 0.0
    assert record["preterminal_cover"]["cell_count"] == 3000
    assert record["preterminal_cover"]["minimum_selected_eigenvalue_lower"] > 0.0
    consequence = record["Gate7_consequence"]
    assert consequence["canonical_earliest_lambda24_zero_exists_in_terminal_cell"] == "CERTIFIED_BY_CONTINUITY"
    assert consequence["unique_or_differentiable_stop_time"] == "NOT_REQUIRED_NOT_CLAIMED"
    assert record["claim_boundary"]["Gate7_geometric_connection_owner"] == "CLOSED"

    with np.load(STOP_DATA) as data:
        intervals = np.asarray(data["preterminal_action_intervals"], dtype=float)
        branches = np.asarray(data["selected_branches"], dtype=int)
        lowers = np.asarray(data["selected_eigenvalue_lower"], dtype=float)
    assert intervals.shape == (3000, 2)
    assert np.all(branches == 24)
    assert np.all(lowers > 0.0)
    assert float(np.min(lowers)) == record["preterminal_cover"]["minimum_selected_eigenvalue_lower"]
    assert _sha256(STOP_DATA) == record["data_SHA256"]


def test_terminal_stop_is_uniformly_transverse_on_final_cone() -> None:
    record = _load(TRANSVERSALITY)
    assert record["validation_passed"] is True
    center = record["terminal_center"]["outward_Dlambda24_of_F_interval"]
    uniform = record["cone_transfer"]["uniform_Dlambda24_of_F_interval"]
    assert center[1] < 0.0
    assert uniform[1] < 0.0
    assert record["cone_transfer"]["strict_negative_margin_lower"] > 0.0
    assert record["consequence"]["terminal_zero_unique_on_the_certified_terminal_flow_cell"] is True
    assert record["consequence"]["local_differentiable_first_stop_time_map"] is True
    assert record["consequence"]["operator_endpoint_motion_prerequisite"] == "CLOSED"


def test_force_kkt_hessian_verdict_fails_closed_at_actual_missing_oracle() -> None:
    record = _load(VERDICT)
    assert record["validation_passed"] is True
    gate = record["Gate7_verdict"]
    assert gate["geometric_connection_or_stop_owner"] == "CLOSED_BY_CANONICAL_FIRST_STOP"
    assert gate["complete_projected_heat_minus_zeta_covector"] == "OPEN_MISSING_ACTION_OWNED_OPERATOR_ORACLE"
    assert gate["same_action_KKT_root"] == "OPEN_AFTER_FORCE_ORACLE"
    assert gate["constrained_physical_Hessian"] == "OPEN_AFTER_KKT_ROOT_AND_SECOND_JET"
    assert gate["Gate7"] == "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE"
    assert gate["FULL_BHSM_COMPLETE"] is False
    assert record["incompatible_historical_route"]["periodic_laplacian_used"] is True
    assert record["incompatible_historical_route"]["different_dense_seed_used"] is True
    assert record["claim_boundary"]["force_value"] == "NOT_CLAIMED"
    assert record["claim_boundary"]["KKT_root"] == "NOT_CLAIMED"
    assert record["claim_boundary"]["physical_Hessian"] == "NOT_CLAIMED"


def test_new_certificate_provenance_hashes_match_disk() -> None:
    for artifact in (_load(BRACKET), _load(STOP), _load(TRANSVERSALITY), _load(VERDICT)):
        for relative, expected in artifact["inputs"].items():
            assert _sha256(ROOT / relative) == expected
