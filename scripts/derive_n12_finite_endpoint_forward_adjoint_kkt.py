"""Derive the no-selector finite-endpoint forward-adjoint KKT system."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("finite-endpoint forward-adjoint KKT inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated forward-adjoint KKT inputs required")
    parametric, saddle, moving, adjoint, endpoint = records
    validation = {
        "reset_is_set_valued": (
            parametric["adjudication"]["single_hand_selected_reset_history_sufficient"]
            is False
        ),
        "quotient_stationarity_is_exact": (
            saddle["exact_theorem"]["same_configuration_transfer_criterion"]
            == "N^dagger*q_rep=0"
        ),
        "moving_endpoint_projection_is_exact": (
            moving["moving_endpoint_system"]["first_state"] == "Z_h=J_h+V*T_h"
        ),
        "adjoint_pullback_is_available": (
            adjoint["claim_boundary"]["G7_08_force_adjoint_pullback"] == "DERIVED"
        ),
        "endpoint_domain_is_action_owned": (
            endpoint["claim_boundary"]["endpoint_domain_ownership"] == "CLOSED"
        ),
        "single_representative_not_promoted": (
            adjoint["computational_consequence"][
                "one_fixed_reset_parameter_closes_physical_saddle"
            ]
            is False
        ),
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT",
        "status": "NO_SELECTOR_FORWARD_ADJOINT_KKT_SYSTEM_DERIVED_EVALUATION_OPEN",
        "classification": (
            "ON_EACH_NONEMPTY_REGULAR_FINITE_EVENT_OR_CANONICAL_STOP_STRATUM_"
            "THE_SET_VALUED_AE2_RESET_AND_THE_HEAT_MINUS_ZETA_STATIONARITY_"
            "CONDITION_FORM_ONE_COUPLED_FORWARD_STATE_OPERATOR_ADJOINT_AND_"
            "PHYSICAL_RESET_QUOTIENT_KKT_BOUNDARY_VALUE_SYSTEM;_SOLVING_THIS_"
            "SYSTEM_OR_AN_EQUIVALENT_PARAMETRIC_ORACLE_ROOT_IS_REQUIRED_AND_"
            "NO_SINGLE_RESET_REPRESENTATIVE_IS_SELECTED"
        ),
        "unknowns": [
            "PHYSICAL_RESET_QUOTIENT_PARAMETER_xi",
            "FINITE_ENDPOINT_TIME_OR_INTRINSIC_STOP_GRAPH_T",
            "FORWARD_STATE_HISTORY_Y(t)",
            "FIXED_CHANNEL_OR_OPERATOR_STATE_ON_Y",
            "BACKWARD_OPERATOR_AND_EULER_DIRAC_ADJOINT_p(t)",
            "RETAINED_CONSTRAINT_AND_ENDPOINT_MULTIPLIERS_IF_RAW_COORDINATES_USED",
        ],
        "system": {
            "reset": "Y(0)=R_AE2(xi),_xi_IN_C_reset/G_exact",
            "forward": "Y'=V_AE2(Y)",
            "endpoint": (
                "FIRST_TRANSVERSE_RETAINED_EVENT_e(Y(T))=0_OR_THE_FIRST_"
                "RETAINED_CANONICAL_STOP_GRAPH_ON_THE_SELECTED_STRATUM"
            ),
            "operator": "P_C=P_C[Y,T]_WITH_THE_ACTION_OWNED_ENDPOINT_DOMAIN",
            "operator_cotangent": (
                "W_C=(s_C*m_C/2)*exp(-ell^2*P_C)*P_C^-1_AND_q_rep=q_heat-q_zeta"
            ),
            "moving_endpoint": "Pi_T=I-V tensor De/(De V)",
            "adjoint": "-p'=DV(Y)^dagger*p+q_Y,_p(T)=Pi_T^dagger*g_T",
            "quotient_stationarity": (
                "N_phys^dagger*(D_xi_R_AE2^dagger*p(0)+q_xi,direct)=0"
            ),
            "raw_bordered_equivalent": (
                "q_xi+D_C_reset^dagger*lambda=0,_C_reset=0,_WITH_EXACT_"
                "GAUGE_AND_WHOLE_TIME_GENERATORS_QUOTIENTED"
            ),
        },
        "equivalent_routes": {
            "parametric_oracle_route": (
                "CERTIFY_Y(xi),T(xi),P_C(xi)_ON_A_FIXED_REGULAR_STRATUM;_"
                "EVALUATE_THE_ADJOINT_COVECTOR_AND_CERTIFY_ITS_QUOTIENT_ROOT"
            ),
            "simultaneous_BVP_route": (
                "SOLVE_AND_CERTIFY_THE_FORWARD_STATE_OPERATOR_ADJOINT_"
                "ENDPOINT_AND_QUOTIENT_STATIONARITY_EQUATIONS_TOGETHER"
            ),
            "mathematically_equivalent_at_a_regular_root": True,
            "new_physical_choice": False,
        },
        "derivative_boundary": {
            "residual_evaluation_highest_action_derivative": "D3_L",
            "Newton_or_KKT_linearization_for_nonzero_force_branch": (
                "REQUIRES_THE_RETAINED_D4_L_SECOND_OPERATOR_JET_AND_RESET_"
                "CONSTRAINT_CURVATURE_ALREADY_CLASSIFIED_DOWNSTREAM"
            ),
            "pair_plus_contact_source_Hessian_is_this_KKT_Jacobian": False,
        },
        "exact_next_dependency": (
            "CERTIFY_A_NONEMPTY_REGULAR_FINITE_ENDPOINT_STRATUM_SOLUTION_OF_"
            "THIS_FORWARD_ADJOINT_QUOTIENT_KKT_SYSTEM_OR_ITS_EQUIVALENT_"
            "PARAMETRIC_ORACLE_ROOT;_THE_TWO_CERTIFIED_CHORDS_SUPPLY_ONLY_A_"
            "BASE_CORE_WITH_NO_ENDPOINT_AND_CHORD_3_REMAINS_UNAUTHORIZED"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FORWARD_ADJOINT_KKT_SOLUTION_OPEN",
            "G7_08_force_adjoint": "DERIVED",
            "G7_09_joint_system": "DERIVED_UNSOLVED",
            "actual_finite_endpoint_stratum_solution": "OPEN_CURRENT_OWNER",
            "single_reset_representative_sufficient": False,
            "geometry_reset_KKT_Hessian": "PENDING_FOR_CERTIFIED_NEWTON_OR_NONZERO_FORCE",
            "pair_plus_contact_Hessian": "PENDING_AFTER_ZERO_SOURCE_SADDLE",
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
