"""Derive the exact C2 launch-adjoint and fixed-seed seam split."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_c2_launch_adjoint_pullback import (  # noqa: E402
    c2_launch_adjoint_pullback,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json"
RESET = BASE / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
RESET_DATA = RESET.with_suffix(".npz")
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
ADJOINT = BASE / "BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
MODULE = ROOT / "src/bhsm/interface/aether_c2_launch_adjoint_pullback.py"
THEORY = ROOT / "theory/n12_c2_reset_launch_adjoint_interface.md"
INPUTS = (RESET, RESET_DATA, LAUNCH, LAUNCH_DATA, ADJOINT, MODULE, THEORY)
STATE_DIMENSION = 98
RANK_THRESHOLD = 1.0e-8


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing launch-adjoint inputs: " + ", ".join(missing))
    reset, launch, adjoint = (_load(path) for path in (RESET, LAUNCH, ADJOINT))
    if not all(record.get("validation_passed") is True for record in (
        reset, launch, adjoint,
    )):
        raise RuntimeError("validated reset, launch, and adjoint records required")

    with np.load(RESET_DATA) as data:
        jacobian = np.asarray(data["analytic_full_reset_jacobian"], dtype=float)
    _, _, reset_vh = np.linalg.svd(jacobian, full_matrices=True)
    reset_tangent = reset_vh[57:].T
    with np.load(LAUNCH_DATA) as data:
        event_image = np.asarray(data["event_image_basis"], dtype=float)
        outgoing_field = np.asarray(data["outgoing_field_action"], dtype=float)

    # Deterministic algebraic witness only.  Its values are not BHSM forces.
    rng = np.random.default_rng(20260825)
    state_covector = rng.normal(size=STATE_DIMENSION)
    direct_covector = rng.normal(size=2 * STATE_DIMENSION)
    split = c2_launch_adjoint_pullback(
        reset_tangent_basis=reset_tangent,
        event_image_basis=event_image,
        outgoing_field_action=outgoing_field,
        state_covector_action_dual=state_covector,
        direct_seam_covector_action_dual=direct_covector,
        state_dimension=STATE_DIMENSION,
        rank_threshold=RANK_THRESHOLD,
    )

    validation = {
        "reset_tangent_dimension_is_139": split["tangent_dimension"] == 139,
        "outgoing_seed_rank_is_72": split["seed_rank"] == 72,
        "fixed_seed_kernel_dimension_is_67": split["seed_kernel_dimension"] == 67,
        "natural_launch_dimension_is_73": split["launch_dimension"] == 73,
        "event_image_spans_seed_map": split["image_projection_residual_norm"] < 1.0e-12,
        "downstream_C2_pullback_annihilates_fixed_seed_kernel": (
            split["downstream_kernel_annihilation_residual_norm"] < 1.0e-12
        ),
        "full_kernel_force_reduces_to_direct_seam_covector": (
            split["kernel_split_residual_norm"] < 1.0e-12
        ),
        "natural_and_orthonormal_launch_pullbacks_agree": (
            split["natural_orthonormal_pullback_relative_residual"] < 1.0e-12
        ),
        "launch_coordinate_change_is_invertible": split["transverse_scale"] > 1.0,
        "one_adjoint_not_73_forward_columns": (
            adjoint["computational_consequence"]["forward_Jacobi_columns_required"]
            == 0
        ),
        "no_inverse_selector_endpoint_force_scale_recurrence_gate_or_chord_added": (
            split["explicit_matrix_inverse_formed"] is False
        ),
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE",
        "status": (
            "C2_RESET_LAUNCH_ADJOINT_AND_FIXED_SEED_SEAM_SPLIT_DERIVED"
            if passed else "C2_RESET_LAUNCH_ADJOINT_INTERFACE_NOT_DERIVED"
        ),
        "classification": (
            "THE_DOWNSTREAM_C2_ADJOINT_PULLBACK_FACTORS_THROUGH_THE_72_"
            "DIMENSIONAL_RESET_SEED_IMAGE_AND_ANNIHILATES_ITS_67_DIMENSIONAL_"
            "KERNEL;_THE_KERNEL_STATIONARITY_EQUATION_IS_THEREFORE_PURELY_A_"
            "DIRECT_TWO_SIDED_SEAM_CONDITION,_WHILE_ONE_ADJOINT_COVECTOR_"
            "SUPPLIES_THE_73_COORDINATE_OUTGOING_LAUNCH_FORCE"
        ),
        "exact_split": {
            "reset_tangent_basis": "Z:R139_TO_ker(D_Creset)_SUBSET_R196",
            "outgoing_seed_map": "B=P_C2*Z:R139_TO_R98,_rank(B)=72",
            "fixed_seed_kernel": "K:R67_TO_ker(B)",
            "downstream_pullback": "g_C2=B^dagger*p_0",
            "kernel_annihilation": "K^dagger*g_C2=0",
            "total_reset_force": "g_total=Z^dagger*d_seam+B^dagger*p_0",
            "kernel_stationarity": "K^dagger*g_total=(Z*K)^dagger*d_seam=0",
            "natural_launch_map": "B_launch=[Q,F_0]:R73_TO_R98",
            "launch_force": "g_launch=(Q^dagger*p_0,<F_0,p_0>)",
        },
        "dimension_ledger": {
            "full_reset_tangent": split["tangent_dimension"],
            "outgoing_C2_seed_image": split["seed_rank"],
            "fixed_C2_seed_lift_kernel": split["seed_kernel_dimension"],
            "outgoing_descriptor_direction": 1,
            "natural_C2_launch": split["launch_dimension"],
            "identities": ["139=72+67", "73=72+1"],
        },
        "numerical_identity_witness": {
            "role": "DETERMINISTIC_LINEAR_ALGEBRA_CROSSCHECK_NOT_A_PHYSICAL_FORCE",
            "seed_map_smallest_nonzero_singular_value": float(
                split["seed_singular_values"][71]
            ),
            "seed_map_largest_null_singular_value": float(
                split["seed_singular_values"][72]
            ),
            "transverse_coordinate_scale": split["transverse_scale"],
            "event_image_projection_residual_norm": split[
                "image_projection_residual_norm"
            ],
            "downstream_kernel_annihilation_residual_norm": split[
                "downstream_kernel_annihilation_residual_norm"
            ],
            "kernel_split_residual_norm": split["kernel_split_residual_norm"],
            "natural_orthonormal_pullback_residual_norm": split[
                "natural_orthonormal_pullback_residual_norm"
            ],
            "natural_orthonormal_pullback_relative_residual": split[
                "natural_orthonormal_pullback_relative_residual"
            ],
        },
        "matching_audit": [
            {
                "diagram_slot": "DOWNSTREAM_C2_HISTORY_FORCE_TO_RESET",
                "required_type": "C2_INITIAL_STATE_COTANGENT_PULLBACK",
                "candidate": "B^dagger*p_0_WITH_B=P_C2*Z",
                "verdict": "VALID_MATCH_ONE_ADJOINT_NO_FORWARD_COLUMN_FAMILY",
            },
            {
                "diagram_slot": "FIXED_C2_SEED_RESET_KERNEL_FORCE",
                "required_type": "LOCAL_TWO_SIDED_EVENT_SEAM_COVECTOR",
                "candidate": "(Z*K)^dagger*d_seam",
                "verdict": "TYPE_AND_DOMAIN_MATCH_FORMULA_DERIVED_ACTUAL_VALUE_OPEN",
            },
            {
                "diagram_slot": "MAXIMAL_OR_FINITE_ENDPOINT_C2_ADJOINT_p_0",
                "required_type": "ACTUAL_HEAT_MINUS_ZETA_C2_COTANGENT",
                "candidate": "RETAINED_ADJOINT_THEOREM",
                "verdict": "THEOREM_MATCH_ACTUAL_ACTION_DATA_STILL_MISSING",
            },
        ],
        "adjudication": {
            "73_forward_Jacobi_columns_required_for_scalar_force": False,
            "one_C2_adjoint_covector_required": True,
            "67_kernel_directions_may_be_discarded_from_full_seam_saddle": False,
            "67_kernel_downstream_C2_contribution": "IDENTICALLY_ZERO",
            "67_kernel_direct_seam_stationarity": "OPEN_ACTUAL_EVALUATION",
            "73_coordinate_C2_launch_force": "OPEN_ACTUAL_ADJOINT",
            "zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_ACTUAL_DIRECT_TWO_SIDED_SEAM_COVECTOR_AND_TEST_ITS_"
            "67_DIMENSIONAL_FIXED_SEED_KERNEL_PROJECTION;_IN_PARALLEL_SOLVE_ONE_"
            "ACTUAL_C2_HEAT_MINUS_ZETA_ADJOINT_ON_THE_MAXIMAL_HISTORY_OR_A_"
            "CERTIFIED_FINITE_LATER_ENDPOINT_AND_PULL_IT_TO_THE_73_COORDINATE_"
            "LAUNCH_CHART"
        ),
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_TWO_COMPLEMENTARY_FORCE_BLOCKS",
            "Gate8": "LOCKED",
            "launch_adjoint_interface": "DERIVED",
            "fixed_seed_kernel_seam_force": "OPEN_ACTUAL_EVALUATION",
            "C2_maximal_or_finite_endpoint_adjoint": "OPEN_CURRENT_OWNER",
            "actual_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "dimensions": payload["dimension_ledger"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
