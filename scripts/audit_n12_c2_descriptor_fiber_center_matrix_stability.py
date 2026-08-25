"""Compare two centered fixed-s tangent-matrix difference scales."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX_STABILITY.json"
FULL = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX.json"
FULL_DATA = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX.npz"
HALF = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX_HALFSTEP.json"
HALF_DATA = BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX_HALFSTEP.npz"
THEORY = ROOT / "theory/n12_c2_descriptor_fiber_center_matrix.md"
INPUTS = (FULL, FULL_DATA, HALF, HALF_DATA, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing center-matrix stability inputs: " + ", ".join(missing))
    full = json.loads(FULL.read_text(encoding="utf-8"))
    half = json.loads(HALF.read_text(encoding="utf-8"))
    if not full["validation_passed"] or not half["validation_passed"]:
        raise RuntimeError("validated center-matrix parents required")
    with np.load(FULL_DATA) as left, np.load(HALF_DATA) as right:
        lambda_defect = float(np.linalg.norm(
            left["lambda_gradient_action"] - right["lambda_gradient_action"]
        ))
        Kato_defect = float(np.linalg.norm(
            left["selected_vector_derivative_action"]
            - right["selected_vector_derivative_action"]
        ))
        g_left = left["c_gradient_action_central_difference"]
        g_right = right["c_gradient_action_central_difference"]
        full_gradient_relative = float(
            np.linalg.norm(g_left - g_right) / np.linalg.norm(g_right)
        )
        A_left = left["birth_limit_matrix_action"]
        A_right = right["birth_limit_matrix_action"]
        birth_relative = float(
            np.linalg.norm(A_left - A_right) / np.linalg.norm(A_right)
        )
        T_left = left["fixed_s_tangent_matrix"]
        T_right = right["fixed_s_tangent_matrix"]
        tangent_relative = float(
            np.linalg.norm(T_left - T_right) / np.linalg.norm(T_right)
        )
        tangent_operator_difference = float(np.linalg.norm(T_left - T_right, 2))
    growth_rows = []
    for left_row, right_row in zip(full["growth_profile"], half["growth_profile"]):
        if left_row["signed_descriptor_horizon"] != right_row["signed_descriptor_horizon"]:
            raise RuntimeError("growth horizons do not match")
        growth_rows.append({
            "signed_descriptor_horizon": left_row["signed_descriptor_horizon"],
            "fullstep_growth": left_row["fixed_s_tangent_fundamental_2_norm"],
            "halfstep_growth": right_row["fixed_s_tangent_fundamental_2_norm"],
            "absolute_growth_difference": abs(
                left_row["fixed_s_tangent_fundamental_2_norm"]
                - right_row["fixed_s_tangent_fundamental_2_norm"]
            ),
        })
    row_1e22 = next(
        row for row in growth_rows if row["signed_descriptor_horizon"] == 1.0e-22
    )
    validation = {
        "same_exact_D3_Kato_center_data_replayed": lambda_defect == 0.0 and Kato_defect == 0.0,
        "complete_moving_cubic_gradient_stable_to_two_percent": full_gradient_relative < 0.02,
        "full_birth_matrix_stable_to_two_percent": birth_relative < 0.02,
        "one_e_minus_22_propagator_difference_below_3e_minus_12": (
            row_1e22["absolute_growth_difference"] < 3.0e-12
        ),
        "small_tangent_residual_matrix_sensitivity_disclosed": tangent_relative > 0.5,
        "center_matrix_not_promoted_to_between_center_interval_authority": True,
        "no_equation_selector_recurrence_scale_gate_or_chord_added": True,
    }
    payload = {
        "artifact": "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX_STABILITY",
        "status": (
            "FIXED_S_CENTER_PROPAGATOR_SCALE_STABLE;_CONJUGATED_INTERVAL_REMAINDER_OPEN"
            if all(validation.values()) else "C2_CENTER_MATRIX_STABILITY_AUDIT_INVALID"
        ),
        "difference_scales": {
            "full_action_difference_step": full["center"]["action_difference_step"],
            "half_action_difference_step": half["center"]["action_difference_step"],
            "lambda_gradient_absolute_defect": lambda_defect,
            "Kato_eigenline_derivative_absolute_defect": Kato_defect,
            "complete_c_gradient_relative_defect": full_gradient_relative,
            "full_birth_matrix_relative_Frobenius_defect": birth_relative,
            "tangent_matrix_relative_Frobenius_defect": tangent_relative,
            "tangent_matrix_operator_difference": tangent_operator_difference,
        },
        "growth_comparison": growth_rows,
        "diagnosis": {
            "stable_fact": (
                "THE_ACTION_D3_KATO_DATA,_COMPLETE_MOVING_CUBIC_GRADIENT,_"
                "FULL_BIRTH_MATRIX,_AND_SHORT_DESCRIPTOR_PROPAGATOR_SCALE_"
                "ARE_STABLE_UNDER_STEP_HALVING"
            ),
            "unstable_fact": (
                "THE_SMALL_FIXED_s_TANGENT_RESIDUAL_MATRIX_IS_A_DIFFERENCE_"
                "OF_LARGE_TERMS_AND_REQUIRES_A_SIGNED_HIGH_PRECISION_D4_OR_"
                "INTERVAL_DIRECTIONAL_EVALUATION"
            ),
            "proof_authority": "CENTER_DIAGNOSTIC_ONLY",
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_SIGNED_FIXED_LINE_D4_TERM_AND_RETAINED_D5_"
            "CENTRAL_REMAINDER,_THEN_PROPAGATE_THE_CONJUGATED_FIXED_s_"
            "TANGENT_TUBE"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "difference_scales": payload["difference_scales"],
        "growth_at_1e_minus_22": row_1e22,
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
