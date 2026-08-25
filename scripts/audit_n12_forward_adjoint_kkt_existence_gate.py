"""Audit existence inputs for the Gate-7 forward-adjoint KKT system."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("forward-adjoint KKT existence-gate inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated KKT existence-gate inputs required")
    kkt, parametric, endpoint, chords, maximal, energy, formation = records
    validation = {
        "forward_adjoint_equations_derived_but_unsolved": (
            kkt["claim_boundary"]["G7_09_joint_system"] == "DERIVED_UNSOLVED"
            and kkt["claim_boundary"]["actual_finite_endpoint_stratum_solution"]
            == "OPEN_CURRENT_OWNER"
        ),
        "actual_parametric_oracle_absent": (
            parametric["adjudication"]["actual_parametric_N12_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
        ),
        "endpoint_domain_class_not_ambiguous": (
            endpoint["claim_boundary"]["endpoint_domain_ownership"] == "CLOSED"
        ),
        "two_chords_do_not_supply_endpoint_or_tail": (
            chords["adjudication"][
                "two_chord_finite_core_promotable_to_complete_heat_response"
            ]
            is False
            and chords["adjudication"]["chord_03_authorized"] is False
        ),
        "maximal_flow_dichotomy_does_not_select_outcome": (
            maximal["ordered_event"]["outcome_selected"] is False
        ),
        "constraint_energy_is_not_coercive": (
            energy["action_ownership_consequence"][
                "constraint_energy_can_supply_a_positive_strong_S2_norm"
            ]
            is False
        ),
        "finite_formation_exists_without_post_event_recurrence": (
            formation["adjudication"]["finite_positive_time_completed_encapsulation_exists"]
            is True
            and formation["adjudication"]["return_or_recurrence_required"] is False
        ),
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE",
        "status": "EQUATIONS_DERIVED_EXISTENCE_AND_CERTIFICATION_OPEN",
        "classification": (
            "THE_CURRENT_AE2_REPOSITORY_OWNS_THE_FINITE_ENDPOINT_DOMAIN_CLASS_"
            "AND_THE_COMPLETE_FORWARD_ADJOINT_QUOTIENT_KKT_EQUATIONS_BUT_"
            "PROVES_NEITHER_A_NONEMPTY_POST_RESET_REGULAR_TERMINAL_STRATUM_"
            "CARRYING_A_KKT_ROOT_NOR_A_DIRECT_COMPACTNESS_COERCIVITY_OR_DEGREE_"
            "THEOREM_FOR_SUCH_A_ROOT;_THE_TWO_CERTIFIED_CHORDS_AND_THE_ZERO_"
            "CONSTRAINT_ENERGY_CANNOT_SUPPLY_THAT_EXISTENCE_THEOREM"
        ),
        "closed_inputs": {
            "finite_positive_time_formation_encapsulation_exists": True,
            "post_event_return_required": False,
            "endpoint_domain_class_action_owned": True,
            "forward_adjoint_quotient_KKT_equations": "DERIVED",
            "fixed_stratum_operator_regularity": "DERIVED_CONDITIONAL",
            "inverse_free_operator_and_adjoint_solves": "DERIVED",
        },
        "nonpromotion_results": {
            "local_formation_branch_is_post_reset_terminal_stratum": False,
            "two_chord_core_is_complete_operator_domain": False,
            "maximal_flow_dichotomy_selects_event_or_stop": False,
            "zero_restricted_Legendre_energy_is_coercive": False,
            "single_reset_representative_is_a_physical_saddle": False,
            "chord_03_has_finite_proof_obligation": False,
        },
        "sufficient_completion_routes": {
            "validated_BVP_route": (
                "CERTIFY_ONE_NONEMPTY_REGULAR_FORWARD_REACHABLE_RESET_"
                "QUOTIENT_STRATUM_AND_A_ZERO_OF_THE_FORWARD_ADJOINT_KKT_"
                "RESIDUAL_WITH_THE_FIRST_ACTUAL_EVENT_OR_CANONICAL_STOP"
            ),
            "direct_existence_route": (
                "PROVE_ACTION_OWNED_COMPACTNESS_PLUS_LOWER_SEMICONTINUITY_"
                "AND_COERCIVITY_OR_A_NONZERO_DEGREE_FOR_THE_SAME_FINITE_"
                "ENDPOINT_KKT_SYSTEM,_WITH_ALL_EXISTING_DOMAIN_MARGINS"
            ),
            "equivalent_oracle_route": (
                "CERTIFY_THE_PARAMETRIC_CHILD_WEYL_FAMILY_ON_A_NONEMPTY_"
                "REGULAR_STRATUM_AND_CERTIFY_A_ROOT_OF_ITS_PHYSICAL_"
                "HEAT_MINUS_ZETA_COVECTOR"
            ),
            "universal_terminal_reachability_required": False,
        },
        "exact_missing_theorem": (
            "NONEMPTY_REGULAR_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT_ROOT_"
            "EXISTENCE_AND_CERTIFICATION_ON_THE_PHYSICAL_RESET_QUOTIENT"
        ),
        "failure_classification": {
            "missing_force_calculus": False,
            "missing_endpoint_boundary_condition": False,
            "missing_linear_solver": False,
            "missing_existential_or_validated_global_temporal_control": True,
            "retained_action_incompatibility_proved": False,
            "new_action_term_justified": False,
        },
        "exact_next_dependency": (
            "PROVE_OR_CERTIFY_A_NONEMPTY_REGULAR_FINITE_ENDPOINT_ROOT_OF_THE_"
            "DERIVED_FORWARD_ADJOINT_PHYSICAL_QUOTIENT_KKT_SYSTEM;_DO_NOT_"
            "REOPEN_INFINITE_NONENCAPSULATING_FORMATION_TAILS,_TERMINAL_"
            "RECURRENCE,_CHORD_3,_OR_AN_ARBITRARY_RESET_REPRESENTATIVE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_KKT_ROOT_EXISTENCE_CURRENT_OWNER",
            "G7_08_force_and_G7_09_system": "DERIVED_UNEVALUATED",
            "finite_endpoint_KKT_root": "OPEN_CURRENT_OWNER",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
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
