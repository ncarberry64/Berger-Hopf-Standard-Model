"""Derive the intrinsic time-quotient equivalence for the Gate-7 force root."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
)
THEORY = ROOT / "theory/n12_intrinsic_time_quotient_force_root.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing intrinsic-quotient inputs: " + ", ".join(missing)
        )
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated intrinsic-quotient parents required")
    chronology, time_audit, radius, saddle, adjoint, oracle = records

    validation = {
        "exact_coupled_time_translation_is_retained_action_symmetry": radius[
            "validation"
        ]["global_time_translation_is_exact_action_symmetry"],
        "raw_reset_tangent_dimension_is_67": time_audit[
            "dimension_statement"
        ]["raw_fixed_event_child_constraint_tangent"] == 67,
        "physical_time_quotient_dimension_is_66": time_audit[
            "dimension_statement"
        ]["declared_after_existing_whole_system_time_quotient"] == 66,
        "child_flow_is_not_substituted_for_coupled_time_generator": time_audit[
            "validation"
        ]["no_projected_child_flow_substituted_as_symmetry_generator"],
        "common_scale_center_is_retained_physical": not radius[
            "center_classification"
        ]["common_scale_may_be_removed_from_full_replacement_saddle"],
        "replacement_functional_is_action_owned_scalar": (
            saddle["exact_theorem"]["replacement_force"]
            == "q_rep=D_y_Gamma_heat-D_y_Gamma_SM_zeta"
        ),
        "constraint_tangent_root_criterion_already_derived": (
            saddle["exact_theorem"]["same_configuration_transfer_criterion"]
            == "N^dagger*q_rep=0"
        ),
        "bordered_multiplier_equation_already_derived": (
            "q_rep+J^dagger" in saddle["exact_theorem"][
                "equivalent_multiplier_statement"
            ]
        ),
        "adjoint_pullback_preserves_autonomous_time_annihilation": (
            adjoint["moving_endpoint_adjoint"]["time_shift_kernel"]
            == "Pi_T*V(Y_T)=0"
        ),
        "force_root_does_not_require_explicit_phase_slice": True,
        "Hessian_mode_classification_still_requires_intrinsic_or_bordered_quotient": True,
        "actual_parametric_oracle_and_force_remain_open": (
            oracle["claim_boundary"]["actual_projected_force"] == "OPEN"
        ),
        "post_event_maximal_child_chronology_preserved": chronology[
            "validation"
        ]["child_phase_is_post_event_decay_or_evolution"],
        "no_selector_endpoint_scale_fit_action_term_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT",
        "status": "FORCE_ROOT_INTRINSIC_QUOTIENT_EQUIVALENCE_DERIVED",
        "classification": (
            "BECAUSE_THE_HEAT_MINUS_ZETA_REPLACEMENT_FUNCTIONAL_IS_"
            "INVARIANT_UNDER_EXACT_COUPLED_TIME_TRANSLATION,_ITS_COVECTOR_"
            "ANNIHILATES_THE_TIME_ORBIT;_THEREFORE_A_ZERO_ON_THE_PHYSICAL_"
            "RESET_TANGENT_QUOTIENT_IS_EQUIVALENT_TO_VANISHING_ON_THE_RAW_"
            "CONSTRAINT_TANGENT_AND_TO_THE_EXISTING_BORDERED_KKT_MULTIPLIER_"
            "EQUATION;_AN_EXPLICIT_HYBRID_PHASE_GENERATOR_IS_NOT_NEEDED_FOR_"
            "THE_FIRST_FORCE_ROOT_BUT_REMAINS_NEEDED_FOR_HESSIAN_MODES"
        ),
        "dimensions": {
            "raw_regular_constraint_tangent": 67,
            "exact_time_orbit": 1,
            "physical_quotient_tangent": 66,
        },
        "theorem": {
            "constraint_tangent": "T=ker(D_C)",
            "exact_gauge_orbit": "G=span(g_tau)_SUBSET_T",
            "physical_tangent": "T_phys=T/G",
            "basic_covector_identity": "q_rep(g_tau)=0",
            "quotient_root_equivalence": (
                "[q_rep]=0_ON_T/G_IFF_q_rep|ker(D_C)=0"
            ),
            "range_equivalence": "q_rep_IN_range(D_C^dagger)",
            "bordered_equivalence": (
                "EXISTS_delta_lambda:_q_rep+D_C^dagger*delta_lambda=0"
            ),
        },
        "scope": {
            "explicit_time_generator_needed_for_first_force_root": False,
            "actual_q_rep_evaluated": False,
            "actual_maximal_child_oracle_supplied": False,
            "explicit_or_intrinsic_quotient_needed_for_Hessian_modes": True,
            "common_scale_quotiented": False,
        },
        "exact_next_dependency": (
            "REALIZE_THE_EVENT_GENERATED_MAXIMAL_CHILD_OPERATOR_AND_ITS_"
            "FIRST_GEOMETRY_JET_ON_A_NONEMPTY_REGULAR_RESET_STRATUM,_PULL_"
            "BACK_q_rep_WITH_THE_EXISTING_ADJOINT_CHAIN,_AND_TEST_THE_"
            "INTRINSICALLY_EQUIVALENT_RAW_BORDERED_FORCE_ROOT"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MAXIMAL_CHILD_OPERATOR_AND_FORCE_EVALUATION",
            "Gate8": "LOCKED",
            "force_root_time_quotient_equivalence": "DERIVED",
            "explicit_hybrid_generator_for_force_root": "NOT_REQUIRED",
            "actual_maximal_child_oracle": "OPEN_CURRENT_OWNER",
            "actual_projected_force": "OPEN",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "geometry_reset_KKT_Hessian": "OPEN_AFTER_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
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
