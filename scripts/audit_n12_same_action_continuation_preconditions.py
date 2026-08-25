"""Audit whether a same-action saddle continuation theorem can start."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json",
    ROOT / "artifacts/BHSM_aether_reset_hessian_matter_cones_v15_93.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("same-action continuation inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated continuation inputs required")
    existence, saddle, force, parametric, energy, historical = records
    validation = {
        "existence_gate_is_current": (
            existence["claim_boundary"]["finite_endpoint_KKT_root"]
            == "OPEN_CURRENT_OWNER"
        ),
        "positive_tangent_Hessian_is_only_a_witness": (
            saddle["actual_N12_reset_witness"][
                "linearized_witness_positive_definite_on_tangent"
            ]
            is True
            and saddle["stage_adjudication"][
                "actual_geometry_reset_KKT_Hessian_available"
            ]
            is False
        ),
        "actual_replacement_force_is_unavailable": (
            force["current_realization_audit"][
                "therefore_current_force_value_or_sign_evaluated"
            ]
            is False
        ),
        "complete_parametric_oracle_is_unavailable": (
            parametric["adjudication"]["actual_parametric_N12_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
        ),
        "constraint_energy_cannot_supply_coercivity": (
            energy["action_ownership_consequence"][
                "constraint_energy_can_supply_a_positive_strong_S2_norm"
            ]
            is False
        ),
        "historical_zero_Hessian_is_constant_map_only": (
            historical["reset_second_variation"]["second_Frechet_derivative"]
            == "D2 R_hat_s=0"
            and historical["reset_second_variation"]["reason"].startswith(
                "constant_reconstruction"
            )
        ),
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS",
        "status": "CONTINUATION_THEOREM_NOT_INITIALIZED_ACTUAL_KKT_DATA_OPEN",
        "classification": (
            "A_HOMOTOPY_OR_IMPLICIT_FUNCTION_CONTINUATION_FROM_THE_CERTIFIED_"
            "LOCAL_ZETA_CASIMIR_ROOT_TO_THE_HEAT_REPLACEMENT_ACTION_REQUIRES_"
            "THE_ACTUAL_COMPLETE_HISTORY_PHYSICAL_QUOTIENT_KKT_HESSIAN_AND_"
            "HEAT_MINUS_ZETA_FORCE_WITH_UNIFORM_DOMAIN_MARGINS;_THE_CURRENT_"
            "DISK_HAS_NEITHER,_AND_ITS_SYNTHETIC_POSITIVE_HESSIAN_WITNESS_AND_"
            "HISTORICAL_CONSTANT_MAP_ZERO_HESSIAN_HAVE_NO_PROMOTION_AUTHORITY"
        ),
        "candidate_homotopy": {
            "functional": (
                "Gamma_s=Gamma_local_zeta+s*(Gamma_SM_heat-Gamma_SM_zeta),_"
                "0<=s<=1"
            ),
            "initial_root": "CERTIFIED_LOCAL_57_ROW_ZETA_CASIMIR_ROOT",
            "target_root": "SAME_ACTION_HEAT_REPLACEMENT_FORWARD_ENDPOINT_SADDLE",
            "local_IFT_requirements": [
                "COMPLETE_FINITE_ENDPOINT_OPERATOR_REALIZATION_AT_s=0",
                "ACTUAL_PHYSICAL_QUOTIENT_CLASSICAL_KKT_HESSIAN_H_0",
                "CERTIFIED_INVERTIBILITY_OF_H_0",
                "ACTUAL_HEAT_MINUS_ZETA_FORCE_q_rep",
            ],
            "global_continuation_requirements": [
                "UNIFORM_INVERSE_BOUND_FOR_THE_PHYSICAL_KKT_JACOBIAN",
                "UNIFORM_ENDPOINT_AND_EXISTING_DOMAIN_MARGINS",
                "FORCE_AND_HESSIAN_LIPSCHITZ_OR_DEGREE_CONTROL",
                "NO_ENDPOINT_STRATUM_SWITCH_WITHOUT_A_RETAINED_STOP_RULE",
            ],
        },
        "nonpromotable_objects": {
            "synthetic_positive_tangent_Hessian": (
                "ALGEBRAIC_NULLSPACE_BORDERED_CROSSCHECK_ONLY_NOT_D2_Gamma_TOTAL"
            ),
            "historical_v15_93_zero_reset_Hessian": (
                "D2_OF_A_CONSTANT_RECONSTRUCTION_MAP_NOT_THE_CURRENT_AE2_"
                "RESET_STRATUM_CURVATURE"
            ),
            "ambient_action_Hessian": (
                "NOT_THE_CONSTRAINT_REDUCED_KKT_HESSIAN_WITH_MULTIPLIER_"
                "CONSTRAINT_CURVATURE_AND_HISTORY_OPERATOR_RESPONSE"
            ),
            "zero_constraint_energy": "NOT_A_COERCIVE_CHARGE_OR_MORSE_FUNCTION",
        },
        "adjudication": {
            "local_implicit_function_theorem_applicable_now": False,
            "global_homotopy_continuation_certified_now": False,
            "Brouwer_or_Leray_Schauder_degree_defined_now": False,
            "continuation_route_invalid_in_principle": False,
            "continuation_route_currently_blocked_by_same_oracle": True,
            "validated_direct_BVP_route_remains_distinct": True,
            "retained_action_incompatibility_proved": False,
        },
        "exact_next_dependency": (
            "EITHER_CERTIFY_A_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT_ROOT_"
            "DIRECTLY,_OR_CONSTRUCT_THE_COMPLETE_s=0_OPERATOR_REALIZATION_"
            "AND_ACTUAL_CONSTRAINT_REDUCED_KKT_HESSIAN_FORCE_AND_UNIFORM_"
            "MARGIN_BOUNDS_NEEDED_TO_START_AND_CONTINUE_Gamma_s_TO_s=1"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_KKT_ROOT_EXISTENCE_CURRENT_OWNER",
            "same_action_continuation_theorem": "OPEN_PRECONDITIONS_MISSING",
            "actual_classical_physical_KKT_Hessian": "OPEN",
            "actual_replacement_force": "OPEN",
            "synthetic_Hessian_promoted": False,
            "historical_constant_reset_Hessian_promoted": False,
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
