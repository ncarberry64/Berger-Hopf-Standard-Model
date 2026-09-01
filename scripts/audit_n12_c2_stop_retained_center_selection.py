"""Select the stronger retained numerical center by correlated defect size.

This is a proof-coordinate choice only.  It changes no action, physical
history selector, endpoint, or observable.  Interval authority remains with
the subsequent Krawczyk enclosure.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
HALF_CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.json"
QUARTER_CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.json"
HALF_RESIDUAL = BASE / "BHSM_N12_C2_STOP_DOP853_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.json"
QUARTER_RESIDUAL = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.json"
HALF_CORRECTION = BASE / "BHSM_N12_C2_STOP_FINE_JACOBIAN_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.json"
QUARTER_CORRECTION = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.json"
HALF_FIRST_HIT = BASE / "BHSM_N12_C2_STOP_DENSE_DESCRIPTOR_FIRST_HIT.json"
QUARTER_FIRST_HIT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json"
RESULT = BASE / "BHSM_N12_C2_STOP_RETAINED_CENTER_SELECTION.json"
INPUTS = (
    HALF_CENTER, QUARTER_CENTER, HALF_RESIDUAL, QUARTER_RESIDUAL,
    HALF_CORRECTION, QUARTER_CORRECTION, HALF_FIRST_HIT, QUARTER_FIRST_HIT,
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing retained center comparison inputs: " + ", ".join(missing))
    half_center, quarter_center, half_residual, quarter_residual, half_correction, quarter_correction, half_hit, quarter_hit = (
        _load(path) for path in INPUTS
    )
    half_y = float(half_correction["summary"]["maximum_ambient_correction_profile_2_norm"])
    quarter_y = float(quarter_correction["summary"]["maximum_ambient_correction_profile_2_norm"])
    half_terminal = float(half_correction["summary"]["terminal_physical_state_correction_2_norm"])
    quarter_terminal = float(quarter_correction["summary"]["terminal_physical_state_correction_2_norm"])
    half_leakage = float(half_correction["summary"]["maximum_macro_tangent_leakage_operator_2_norm"])
    quarter_leakage = float(quarter_correction["summary"]["maximum_macro_tangent_leakage_operator_2_norm"])
    validation = {
        "both_centers_use_same_retained_action_field": (
            half_center["method"]
            == quarter_center["method"]
            == "FIXED_DOP853_ON_RETAINED_DENOMINATOR_FREE_ACTION_ARCLENGTH_FIELD"
            and quarter_center["action_jet_realization"]
            == "RETAINED_COMBINED_DIRECTION_DELTA_96_POINT_ACTION"
            and half_residual["construction"]["field"]
            == quarter_residual["construction"]["field"]
            == "RETAINED_NORMALIZED_CANCELLED_BHSM_EULER_DIRAC_FIELD"
        ),
        "both_stored_centers_have_exact_polynomial_first_hits": (
            half_hit["validation_passed"] is True
            and quarter_hit["validation_passed"] is True
        ),
        "quarter_correlated_correction_is_smaller": quarter_y < half_y,
        "quarter_terminal_correction_is_smaller": quarter_terminal < half_terminal,
        "quarter_matched_fine_Jacobian_leakage_is_smaller": quarter_leakage < half_leakage,
        "quarter_path_keeps_branch_24": quarter_residual["summary"]["selected_branches_seen"] == [24],
        "quarter_path_keeps_positive_gap_and_b_psi": (
            float(quarter_residual["summary"]["minimum_selected_eigenline_gap"]) > 0.0
            and float(quarter_residual["summary"]["minimum_b_psi"]) > 0.0
        ),
        "selection_is_proof_coordinate_only_not_physical_selector": True,
        "interval_shadowing_authority_not_claimed": True,
    }
    payload = {
        "artifact": "BHSM_N12_C2_STOP_RETAINED_CENTER_SELECTION",
        "status": "QUARTER_STEP_RETAINED_CENTER_SELECTED_FOR_KRAWCZYK_ENCLOSURE",
        "selection_rule": "MINIMIZE_MATCHED_CORRELATED_GREEN_CORRECTION_AMONG_RETAINED_CENTERS",
        "selected_center": QUARTER_CENTER.relative_to(ROOT).as_posix(),
        "comparison": {
            "half_step": {
                "fixed_step": float(half_center["integrator"]["fixed_action_step"]),
                "pointwise_Gauss12_residual_max": float(half_residual["summary"]["maximum_augmented_rate_residual_2_norm"]),
                "correlated_correction_max": half_y,
                "terminal_state_correction": half_terminal,
                "macro_tangent_leakage": half_leakage,
            },
            "quarter_step": {
                "fixed_step": float(quarter_center["integrator"]["fixed_action_step"]),
                "pointwise_Gauss12_residual_max": float(quarter_residual["summary"]["maximum_augmented_rate_residual_2_norm"]),
                "correlated_correction_max": quarter_y,
                "terminal_state_correction": quarter_terminal,
                "macro_tangent_leakage": quarter_leakage,
            },
            "correlated_correction_reduction_factor": half_y / quarter_y,
            "terminal_correction_reduction_factor": half_terminal / quarter_terminal,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "numerical_proof_center_selected": True,
            "finite_interval_history_certified": False,
            "Gate7": "ACTIVE_KRAWCZYK_RADII_AND_MARGIN_TRANSFER",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
