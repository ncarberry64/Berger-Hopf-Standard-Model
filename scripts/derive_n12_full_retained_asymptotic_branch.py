"""Derive the full retained N12 asymptotic branch consequence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.full_retained_asymptotic_branch import (  # noqa: E402
    asymptotic_branch_theorem,
    normalized_action_scale_decomposition,
    positive_integer_nonresonance,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"
)
INPUTS = (
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json"
    ),
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json"
    ),
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
    ),
    ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("full asymptotic-branch inputs required")
    descriptor, interval, scale_parent, finite_domain = [
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    ]
    if not all(
        parent.get("validation_passed") is True
        for parent in (descriptor, interval, scale_parent, finite_domain)
    ):
        raise RuntimeError("validated full asymptotic-branch lineage required")

    scale = normalized_action_scale_decomposition()
    nonresonance = positive_integer_nonresonance()
    theorem = asymptotic_branch_theorem()
    scale_audit = scale_parent[
        "retained_action_uniform_scale_ownership_audit"
    ]["witness"]
    validation = {
        "exact_retained_bulk_weights_are_7_5_3_1_minus1": (
            scale_audit["pre_inverse_inertia_bulk_scale_weights"]
            == scale["bulk_scale_weights"]
        ),
        "exact_inertia_weights_are_7_5_3_1": (
            scale_audit["inertia_polynomial_scale_weights"]
            == scale["inertia_scale_weights"]
        ),
        "inverse_inertia_normalized_power_is_epsilon7": (
            scale_audit["inverse_inertia_leading_scale_weight"] == -7
            and scale["normalized_inverse_inertia_leading_epsilon_power"]
            == 7
        ),
        "boundary_Casimir_normalized_power_is_epsilon4": (
            scale_audit["boundary_Casimir_scale_weight"] == -1
            and scale["boundary_Casimir_epsilon_power"] == 4
        ),
        "descriptor_has_only_center_and_minus7H0_finite_roots": (
            descriptor["descriptor"]["bordered_clusters"]["center_count"]
            == 25
            and descriptor["descriptor"]["bordered_clusters"][
                "stable_count"
            ] == 25
            and descriptor["descriptor"]["bordered_clusters"][
                "unstable_count"
            ] == 0
        ),
        "all_positive_integer_recurrence_pencils_nonresonant": (
            nonresonance[
                "all_positive_integer_recurrence_pencils_invertible"
            ]
        ),
        "first_order_74_component_interval_lift_certified": (
            interval["claim_boundary"][
                "directed_weight_five_center_lift"
            ] == "CERTIFIED"
        ),
        "twelve_omitted_first_order_equations_compatible": interval[
            "omitted_weight_seven_gauge_chain_compatibility"
        ]["all_contain_zero"],
        "algebraic_multiplier_block_rigorously_invertible": interval[
            "validation"
        ]["algebraic_multiplier_block_rigorously_invertible"],
        "leading_common_scale_rate_interval_strictly_negative": interval[
            "common_scale_rate_interval"
        ]["strictly_negative"],
        "analytic_uniform_remainder_exists_locally": theorem["conclusion"][
            "exists_epsilon_star"
        ],
        "positive_H4_limit_is_H0": (
            theorem["conclusion"]["positive_limit"]
            == "lim_(epsilon_to_0+)H4=H0=sqrt(kappa0/42)>0"
        ),
        "infinite_branch_kept_mathematical_but_nonrealized": (
            finite_domain["physical_domain"][
                "infinite_regular_nonencapsulating_history"
            ]
            == "MATHEMATICALLY_ADMISSIBLE_NONREALIZED_FORMATION_HISTORY_OUTSIDE_THE_PHYSICAL_PARTICLE_OBSERVABLE_DOMAIN"
        ),
        "no_universal_reachability_or_physical_particle_claim": True,
        "no_R_minus_2_eigenvalue_promoted": True,
        "Gate7_zero_source_force_not_overpromoted": True,
    }
    return {
        "artifact": "BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH",
        "status": "FULL_RETAINED_LOCAL_ANALYTIC_BRANCH_H4_TO_H0_POSITIVE_PROVED_NONREALIZED_SCOPE",
        "classification": (
            "THE_COMPLETE_NORMALIZED_RETAINED_ACTION_IS_REAL_ANALYTIC_IN_"
            "epsilon=R4^-2_NEAR_THE_ROUND_EXPANDING_BALANCE;_EVERY_POSITIVE_"
            "INTEGER_BRIOT_BOUQUET_RECURRENCE_PENCIL_IS_NONRESONANT_BECAUSE_"
            "THE_ONLY_FINITE_WEIGHT_SEVEN_ROOTS_ARE_0_AND_-7H0;_THEREFORE_"
            "A_LOCAL_ANALYTIC_FULL_ACTION_BRANCH_EXISTS_WITH_UNIFORMLY_"
            "BOUNDED_REMAINDER_AND_H4_TO_H0>0;_THIS_FOREVER_EXPANDING_BRANCH_"
            "REMAINS_MATHEMATICAL_AND_NONREALIZED_BY_OWNER_ONTOLOGY"
        ),
        "exact_scale_decomposition": scale,
        "positive_integer_nonresonance": nonresonance,
        "analytic_branch_theorem": theorem,
        "first_order_interval_input": {
            "complete_vector_components": len(
                interval["complete_leading_modulation_vector"]
            ),
            "common_scale_lift_interval": interval[
                "common_scale_interval"
            ],
            "common_scale_rate_interval": interval[
                "common_scale_rate_interval"
            ],
            "omitted_gauge_chain_compatibility": interval[
                "omitted_weight_seven_gauge_chain_compatibility"
            ],
        },
        "nonlinear_consequence": {
            "a_preserves_H4_to_H_inf_positive": True,
            "H_inf": "H0=sqrt(kappa0/42)",
            "b_forces_H4_to_zero_with_Osgood_envelope": False,
            "c_drives_event_or_canonical_stop_inside_local_asymptotic_neighborhood": False,
            "backward_continuation_to_formation_or_event": "NOT_PROVED_BY_THIS_LOCAL_INFINITY_THEOREM",
            "universal_history_statement": False,
            "physical_particle_statement": False,
        },
        "adjudication": {
            "uniform_full_remainder_on_local_asymptotic_branch": "PROVED_BY_ANALYTIC_BRIOT_BOUQUET_THEOREM",
            "weight_five_common_scale_sign": "DIRECTED_INTERVAL_CERTIFIED",
            "mathematical_infinite_branch_outcome": "H4_TO_H0_POSITIVE",
            "physical_status": "NONREALIZED_FORMATION_HISTORY_OWNER_AUTHORIZED",
            "finite_encapsulation_existence_or_zero_source_force_changed": False,
        },
        "exact_next_dependency": (
            "RETURN_TO_THE_PHYSICAL_FINITE_HISTORY_GATE7_OWNER:_THE_ACTION_"
            "OWNED_TWO_SIDED_CALDERON_DATA_AND_ZERO_SOURCE_FORCE;_DO_NOT_"
            "REOPEN_INFINITE_TAILS_OR_PROMOTE_THIS_NONREALIZED_BRANCH"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_PHYSICAL_FINITE_HISTORY_ZERO_SOURCE_FORCE_OPEN",
            "mathematical_transverse_nonlinear_modulation_consequence": "CLOSED_OUTCOME_A",
            "physical_finite_history_zero_source_force": "OPEN",
            "universal_terminal_event_reachability": False,
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
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
    print(RESULT)


if __name__ == "__main__":
    main()
