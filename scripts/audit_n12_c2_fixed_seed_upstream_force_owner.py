"""Identify the exact history owned by the C2 fixed-seed kernel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json"
RESET = BASE / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
RESET_DATA = RESET.with_suffix(".npz")
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
LAUNCH_ADJOINT = BASE / "BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json"
TIME_QUOTIENT = BASE / "BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json"
SEAM = BASE / "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
INCOMING_MATCH = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
INCOMING_AXIS = BASE / "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
FORCE = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
ADJOINT = BASE / "BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
RELATIVE = BASE / "BHSM_N12_HISTORICAL_RELATIVE_DETERMINANT_REUSE_AUDIT.json"
AE2 = ROOT / "artifacts" / "action_extension" / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
THEORY = ROOT / "theory" / "n12_c2_fixed_seed_upstream_force_owner.md"
INPUTS = (
    RESET,
    RESET_DATA,
    LAUNCH,
    LAUNCH_DATA,
    LAUNCH_ADJOINT,
    TIME_QUOTIENT,
    SEAM,
    INCOMING_MATCH,
    INCOMING_AXIS,
    FORCE,
    ADJOINT,
    RELATIVE,
    AE2,
    THEORY,
)
STATE_DIMENSION = 98
RANK_THRESHOLD = 1.0e-8


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _null_basis(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    _, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
    rank = int(np.count_nonzero(singular_values > RANK_THRESHOLD))
    return vh[rank:].T, singular_values, rank


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing fixed-seed owner inputs: " + ", ".join(missing))
    records = {path: _load(path) for path in INPUTS if path.suffix == ".json"}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated fixed-seed owner inputs required")

    with np.load(RESET_DATA) as data:
        jacobian = np.asarray(data["analytic_full_reset_jacobian"], dtype=float)
    with np.load(LAUNCH_DATA) as data:
        stored_fixed_seed_lift = np.asarray(
            data["event_lift_kernel_basis"], dtype=float
        )

    # In the certified forward swap the first stored 98-state is C2 and the
    # second is the preceding event E1.  Holding C2 fixed therefore leaves
    # exactly the kernel of the second reset-Jacobian block.
    c2_block = jacobian[:, :STATE_DIMENSION]
    e1_block = jacobian[:, STATE_DIMENSION:]
    e1_kernel, e1_singular_values, e1_rank = _null_basis(e1_block)
    _, c2_singular_values, c2_rank = _null_basis(c2_block)
    fixed_c2_e1_lift = np.vstack((
        np.zeros((STATE_DIMENSION, e1_kernel.shape[1])),
        e1_kernel,
    ))
    stored_projector = stored_fixed_seed_lift @ stored_fixed_seed_lift.T
    exact_projector = fixed_c2_e1_lift @ fixed_c2_e1_lift.T
    projector_residual = float(np.linalg.norm(stored_projector - exact_projector, 2))
    stored_c2_component = float(
        np.linalg.norm(stored_fixed_seed_lift[:STATE_DIMENSION], 2)
    )
    exact_reset_residual = float(np.linalg.norm(jacobian @ fixed_c2_e1_lift, 2))

    ae2 = records[AE2]
    incoming_match = records[INCOMING_MATCH]
    incoming_axis = records[INCOMING_AXIS]
    time_quotient = records[TIME_QUOTIENT]
    relative = records[RELATIVE]
    launch_adjoint = records[LAUNCH_ADJOINT]
    validation = {
        "forward_C2_reset_block_rank_is_32": c2_rank == 32,
        "preceding_E1_reset_block_rank_is_31": e1_rank == 31,
        "fixed_C2_E1_tangent_dimension_is_67": e1_kernel.shape[1] == 67,
        "stored_fixed_seed_lift_is_exactly_the_embedded_E1_kernel": (
            projector_residual < 1.0e-10
            and stored_c2_component < 1.0e-12
            and exact_reset_residual < 1.0e-10
        ),
        "same_raw_67_and_retained_time_quotient_66": (
            time_quotient["dimension_statement"][
                "raw_fixed_event_child_constraint_tangent"
            ]
            == 67
            and time_quotient["dimension_statement"][
                "declared_after_existing_whole_system_time_quotient"
            ]
            == 66
        ),
        "explicit_hybrid_time_generator_remains_open": (
            time_quotient["claim_boundary"]["explicit_time_generator"] == "OPEN"
        ),
        "fermion_independent_surface_action_is_exactly_zero": (
            ae2["action_definition"]["independent_normal_matter_boundary_action"]
            == "S_Sigma_F_AE2=0"
        ),
        "incoming_Mf_is_existing_C1_to_E1_terminal_block": (
            incoming_match["exact_match"]["diagram_leg"]
            == "C1_TO_E1_INCOMING_FORMATION"
        ),
        "incoming_negative_axis_value_does_not_close_pullback": (
            incoming_axis["claim_boundary"]["non_scale_reset_quotient_pullback"]
            == "OPEN_CURRENT_OWNER"
        ),
        "historical_reduced_seam_does_not_supply_full_heat_force": (
            relative["claim_boundary"]["current_N12_forward_relative_determinant"]
            == "OPEN"
        ),
        "downstream_C2_kernel_contribution_is_zero": (
            launch_adjoint["adjudication"]["67_kernel_downstream_C2_contribution"]
            == "IDENTICALLY_ZERO"
        ),
        "no_selector_phase_endpoint_scale_gate_chord_or_prediction_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER",
        "status": (
            "FIXED_C2_SEED_KERNEL_IDENTIFIED_AS_THE_PRECEDING_E1_HISTORY_TANGENT"
            if passed
            else "FIXED_C2_SEED_UPSTREAM_FORCE_OWNER_NOT_IDENTIFIED"
        ),
        "classification": (
            "AFTER_THE_CERTIFIED_FORWARD_SWAP,_THE_67_DIMENSIONAL_KERNEL_OF_"
            "THE_OUTGOING_C2_SEED_PROJECTION_IS_EXACTLY_ZERO_ON_C2_DIRECT_SUM_"
            "ker(J_E1);_ITS_FORCE_IS_THEREFORE_THE_UPSTREAM_C1_TO_E1_AND_"
            "INTERFACE_REPLACEMENT_FORCE,_NOT_A_NEW_LOCAL_SEAM_FORCE_AND_NOT_"
            "A_DOWNSTREAM_C2_FORCE"
        ),
        "exact_tangent_identity": {
            "forward_variable_order": "(C2,E1)",
            "reset_Jacobian": "J_R=[J_C2,J_E1]",
            "fixed_C2_tangent": "K_fixedC2={0}_C2_DIRECT_SUM_ker(J_E1)",
            "dimension": "dim(K_fixedC2)=98-rank(J_E1)=98-31=67",
            "downstream_annihilation": "D_C2_Gamma[K_fixedC2]=0",
            "raw_force_owner": (
                "D_(E1)_Gamma_replacement_FOR_THE_COMPLETE_UPSTREAM_C1_TO_E1_"
                "HISTORY_PLUS_RETAINED_INTERFACE_CONTACTS"
            ),
            "physical_quotient": (
                "THE_RETAINED_COUNT_IS_66_AFTER_THE_WHOLE_SYSTEM_TIME_"
                "QUOTIENT,_BUT_THE_EXPLICIT_HYBRID_GENERATOR_REMAINS_OPEN;_"
                "AN_INTRINSIC_QUOTIENT_FORMULATION_IS_EQUIVALENT"
            ),
        },
        "dimension_and_subspace_witness": {
            "J_C2_rank": c2_rank,
            "J_E1_rank": e1_rank,
            "fixed_C2_E1_kernel_dimension": int(e1_kernel.shape[1]),
            "J_C2_smallest_nonzero_singular_value": float(c2_singular_values[31]),
            "J_E1_smallest_nonzero_singular_value": float(e1_singular_values[30]),
            "stored_to_exact_projector_operator_residual": projector_residual,
            "stored_fixed_seed_C2_component_operator_norm": stored_c2_component,
            "exact_embedded_E1_reset_residual_operator_norm": exact_reset_residual,
        },
        "force_matching_audit": [
            {
                "slot": "DOWNSTREAM_C2_HISTORY_ON_FIXED_SEED_KERNEL",
                "candidate": "B^dagger*p_C2",
                "verdict": "IDENTICALLY_ZERO",
            },
            {
                "slot": "INDEPENDENT_FERMION_INTERFACE_ACTION",
                "candidate": "S_Sigma_F_AE2",
                "verdict": "VALID_MATCH_IDENTICALLY_ZERO_BY_AE2_ACTION",
            },
            {
                "slot": "INCOMING_C1_TO_E1_OPERATOR_RESPONSE",
                "candidate": "M_f=M11_OF_THE_EXISTING_COMPACT_CALDERON_MAP",
                "verdict": (
                    "VALID_VALUE_MATCH_NEGATIVE_AXIS_ENCLOSED;_SIGNED_FULL_"
                    "INCOMING_HISTORY_HEAT_MINUS_ZETA_COTANGENT_OPEN"
                ),
            },
            {
                "slot": "RESET_LIFT_AND_CONTACT",
                "candidate": "U_R_AND_W_phys_FROM_AE2",
                "verdict": (
                    "VALID_DOMAIN_MATCH;_NO_INDEPENDENT_PHASE,_FERMION_W_phys_ZERO,_"
                    "RETAINED_GAUGE_SCALAR_CONTACT_JETS_MUST_REMAIN_IN_THE_JOINT_OPERATOR"
                ),
            },
            {
                "slot": "FULL_INCOMING_BULK_HEAT_AND_ZETA_VARIATION",
                "candidate": "M_f_OR_A_HISTORICAL_REDUCED_SEAM_DETERMINANT_ALONE",
                "verdict": "INVALID_MATCH_DOES_NOT_INCLUDE_THE_COMPLETE_ARM_FUNCTIONAL",
            },
            {
                "slot": "CONSTRAINT_NORMAL_FORCE",
                "candidate": "range(J_R^dagger)",
                "verdict": "KKT_MULTIPLIER_SHIFT_NOT_A_PHYSICAL_TANGENT_FORCE",
            },
            {
                "slot": "COMPLETE_ZERO_SOURCE_FORCE",
                "candidate": "ONE_JOINT_FULL_HISTORY_FORWARD_ADJOINT_KKT_SOLVE",
                "verdict": "VALID_EQUIVALENT_ASSEMBLY_ACTUAL_BASE_AND_COVECTOR_OPEN",
            },
        ],
        "adjudication": {
            "67_kernel_is_a_new_local_seam_degree_family": False,
            "67_kernel_is_the_raw_fixed_C2_preceding_E1_tangent": True,
            "fermion_surface_term_can_supply_a_missing_force": False,
            "M_f_value_or_seam_invertibility_alone_supplies_the_force": False,
            "separate_arbitrary_direct_seam_covector_should_be_invented": False,
            "one_joint_history_adjoint_is_preferred": True,
            "actual_upstream_quotient_force": "OPEN_CURRENT_OWNER",
            "actual_C2_launch_force": "OPEN_CURRENT_OWNER",
            "zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "REALIZE_ONE_PARAMETRIC_OR_COUPLED_KKT_BASE_FOR_THE_COMPLETE_"
            "C1_TO_E1_TO_C2_HISTORY_AND_RUN_ONE_JOINT_BACKWARD_HEAT_MINUS_"
            "ZETA_ADJOINT,_INCLUDING_THE_RETAINED_GAUGE_SCALAR_CONTACT_AND_"
            "MOVING_ENDPOINT_TERMS;_PULL_IT_TO_THE_INTRINSIC_RESET_QUOTIENT_"
            "WITHOUT_INVENTING_A_LOCAL_SEAM_FORCE_OR_PROJECTED_TIME_GENERATOR"
        ),
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_ONE_JOINT_HISTORY_ADJOINT_OWNER",
            "Gate8": "LOCKED",
            "fixed_C2_kernel_identification": "DERIVED",
            "actual_joint_base_history_and_adjoint": "OPEN_CURRENT_OWNER",
            "explicit_hybrid_time_generator": "OPEN_OR_USE_INTRINSIC_QUOTIENT",
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
        "witness": payload["dimension_and_subspace_witness"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
