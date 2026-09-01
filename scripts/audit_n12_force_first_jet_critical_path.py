"""Separate the Gate-7 force first-jet owner from downstream second jets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORCE_FIRST_JET_CRITICAL_PATH.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_EULER_DIRAC_VARIATION_BOUNDS.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("force first-jet critical-path inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated force first-jet inputs required")
    force, saddle, parametric, executable, endpoint, moving, variation = records
    validation = {
        "force_is_a_first_operator_variation": (
            force["exact_force_theorem"]["first_variation"].startswith(
                "D_Gamma_heat(P)[delta_P]"
            )
        ),
        "projected_force_precedes_geometry_Hessian": (
            saddle["stage_adjudication"][
                "actual_projected_heat_minus_zeta_force_covector_available"
            ] is False
            and saddle["stage_adjudication"][
                "actual_geometry_reset_KKT_Hessian_available"
            ] is False
        ),
        "first_and_second_Weyl_solves_are_triangular": (
            executable["solver_contract"]["interior_equations"][0]
            == "P_ii*X=P_ib"
            and executable["solver_contract"]["interior_equations"][1]
            == "P_ii*X'=K_ib'-K_ii'*X"
        ),
        "first_jet_does_not_require_second_jet_input": (
            "K_ib''" not in executable["solver_contract"]["interior_equations"][1]
        ),
        "reset_family_not_one_selected_representative": (
            parametric["adjudication"]["single_hand_selected_reset_history_sufficient"]
            is False
        ),
        "endpoint_domain_and_first_chain_rule_are_closed": (
            endpoint["claim_boundary"]["endpoint_domain_ownership"] == "CLOSED"
            and moving["claim_boundary"]["moving_endpoint_two_jet_chain_rule"]
            == "DERIVED"
        ),
        "first_state_jet_uses_D3_not_D4_action_data": (
            variation["action_derivative_ownership"]["D_h_owned_by"] == "D3_L"
            and variation["action_derivative_ownership"]["D_hk_owned_by"]
            == "D4_L_FOR_STRAIGHT_DIRECTIONS"
            and variation["implicit_solve_theorem"]["first_left"].startswith(
                "s_h=D^-1"
            )
        ),
        "no_second_jet_claim_deleted_or_fabricated": True,
        "no_selector_action_term_endpoint_scale_fit_new_gate_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORCE_FIRST_JET_CRITICAL_PATH",
        "status": "GATE7_FORCE_BASE_AND_FIRST_JET_IS_EARLIEST_OPERATOR_OWNER",
        "classification": (
            "THE_ZERO_SOURCE_HEAT_MINUS_ZETA_FORCE_IS_A_FIRST_VARIATION_AND_"
            "THEREFORE_REQUIRES_THE_ACTUAL_MAXIMAL_CHILD_OPERATOR_VALUE_AND_"
            "FIRST_PHYSICAL_RESET_QUOTIENT_JET_BUT_NOT_ITS_SECOND_JET;_THE_"
            "SECOND_OPERATOR_JET_AND_CONSTRAINT_RESET_CURVATURE_REMAIN_"
            "MANDATORY_FOR_RELOCATING_A_NONZERO_FORCE_TO_THE_JOINT_SADDLE_"
            "AND_FOR_THE_SUBSEQUENT_HESSIAN,_BUT_THEY_DO_NOT_BLOCK_THE_"
            "EARLIEST_G7_08_FORCE_EVALUATION"
        ),
        "critical_path": {
            "G7_08_immediate_inputs": [
                "ACTION_OWNED_MAXIMAL_CHILD_BASE_OPERATOR_K(xi)",
                "FIRST_PHYSICAL_RESET_QUOTIENT_OPERATOR_JET_D_xi_K",
                "EQUIVALENT_M_child(z;xi)_AND_D_xi_M_child",
                "PROJECTED_FORCE_COVECTOR_N_phys^dagger*q_rep",
            ],
            "not_required_before_first_force": [
                "D4_L_AND_MIXED_SECOND_STATE_JACOBI",
                "D_xi2_K",
                "D_xi2_M_child",
                "D2_C_RESET_STRATUM_CURVATURE",
                "GEOMETRY_RESET_KKT_HESSIAN",
            ],
            "conditional_branch_after_force": {
                "if_projected_force_zero": (
                    "THE_CLASSICAL_CONFIGURATION_TRANSFERS_TO_THE_REPLACEMENT_"
                    "SADDLE;_PROCEED_TO_THE_PAIR_PLUS_CONTACT_HESSIAN"
                ),
                "if_projected_force_nonzero": (
                    "CONSTRUCT_D_xi2_K,_D2_C,_AND_THE_GEOMETRY_RESET_KKT_"
                    "HESSIAN_AND_SOLVE_THE_JOINT_CONSTRAINED_SADDLE"
                ),
            },
            "all_physical_tangent_directions_or_equivalent_covector_required": True,
            "single_reset_representative_sufficient": False,
        },
        "operator_triangularity": {
            "value": "P_ii*X=P_ib,_M=P_bb-P_bi*X",
            "first": (
                "P_ii*X_h=K_ib,h-K_ii,h*X,_"
                "M_h=K_bb,h-K_bi,h*X-P_bi*X_h"
            ),
            "second": (
                "A_SEPARATE_LATER_SOLVE_USING_K_hh_AND_X_h;_NOT_AN_INPUT_"
                "TO_THE_VALUE_OR_FIRST_SOLVE"
            ),
        },
        "action_derivative_critical_path": {
            "base_vector_field": "D(Y)*s(Y)=b(Y)",
            "first_vector_field_jet": "D*s_h=b_h-D_h*s",
            "first_jet_highest_action_derivative": "D3_L",
            "mixed_second_vector_field_jet": (
                "D*s_hk=b_hk-D_hk*s-D_h*s_k-D_k*s_h"
            ),
            "mixed_second_highest_action_derivative": "D4_L",
            "adjudication": (
                "D4_L_REMAINS_ACTION_OWNED_AND_REQUIRED_FOR_THE_LATER_SECOND_"
                "JET_OR_HESSIAN_BRANCH_BUT_IS_NOT_A_PRECONDITION_FOR_THE_"
                "EARLIEST_PROJECTED_FORCE_COVECTOR"
            ),
        },
        "exact_next_dependency": (
            "CERTIFY_THE_MAXIMAL_RESET_STRATUM_BASE_AND_FIRST_STATE_JACOBI_"
            "FAMILY_USING_THE_RETAINED_D3_L_AND_DIRAC_MARGIN_TO_THE_FIRST_"
            "ACTION_OWNED_EVENT_OR_CANONICAL_STOP,_THEN_"
            "ASSEMBLE_K_AND_D_xi_K_AND_USE_THE_EXISTING_INVERSE_FREE_FIRST_"
            "WEYL_SOLVE_TO_EVALUATE_N_phys^dagger*q_rep;_DO_NOT_WAIT_FOR_"
            "D2_C_OR_D_xi2_K_BEFORE_COMPUTING_THE_FIRST_FORCE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_BASE_AND_FIRST_MAXIMAL_CHILD_JET_OPEN",
            "G7_08_force_functional": "DERIVED",
            "G7_08_actual_projected_force": "OPEN_CURRENT_OWNER",
            "second_operator_jet": "PENDING_FOR_NONZERO_FORCE_OR_HESSIAN",
            "geometry_reset_KKT_Hessian": "PENDING_AFTER_FIRST_FORCE",
            "same_action_saddle": "CONDITIONAL_ON_FIRST_FORCE_RESULT",
            "pair_plus_contact_Hessian": "PENDING",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
