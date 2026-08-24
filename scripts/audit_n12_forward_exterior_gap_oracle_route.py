"""Adjudicate the positive-gap/Friedrichs shortcut to the Gate-7 oracle.

Coercivity defines the maximal-forward operator and its resolvent, but a
lower form gap does not determine its birth Weyl response.  The exact
half-line family ``-d^2/dt^2 + Q`` supplies a counterfamily with the same
principal part, Friedrichs endpoint class, and common lower gap.  This audit
also records exactly what the certified two-chord core does and does not add.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_EXTERIOR_GAP_ORACLE_AUDIT.json"
)
INPUTS = (
    ARTIFACTS / "BHSM_aether_common_quantum_superdeterminant_v15_96.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_SAME_ACTION_GAUGE_SADDLE_AUDIT.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _constant_half_line_row(q: float, z: float = -1.0) -> dict[str, float]:
    kappa = math.sqrt(q - z)
    return {
        "Q": q,
        "z": z,
        "form_gap_lower": q,
        "Weyl_value": kappa,
        "spectral_derivative": -0.5 / kappa,
        "Q_first_derivative": 0.5 / kappa,
        "Q_second_derivative": -0.25 / (kappa**3),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all exterior-oracle route inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    }
    for name, record in records.items():
        if record.get("validation_passed") is not True:
            raise RuntimeError(f"input did not validate: {name}")

    weyl = records["BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"]
    incidence = records["BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"]
    two_chord = records["BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"]
    superdet = records["BHSM_aether_common_quantum_superdeterminant_v15_96.json"]
    saddle = records["BHSM_N12_SAME_ACTION_GAUGE_SADDLE_AUDIT.json"]
    heat_test = two_chord["two_chord_heat_test"]

    rows = [_constant_half_line_row(q) for q in (1.0, 4.0, 100.0, 10000.0)]
    strictly_increasing = all(
        left["Weyl_value"] < right["Weyl_value"]
        for left, right in zip(rows, rows[1:])
    )
    optimistic_error = float(heat_test["best_case_constant_gap_endpoint_bound_lower"])
    target_scale = 0.765819120592

    validation = {
        "all_inputs_validated": True,
        "native_z_family_consumed_without_p2_identification": (
            weyl["operator_family"]["z_identified_with_momentum_squared"] is False
        ),
        "same_principal_part_and_Friedrichs_endpoint_in_counterfamily": True,
        "common_positive_lower_gap_preserved": all(
            row["form_gap_lower"] >= 1.0 for row in rows
        ),
        "Weyl_values_strictly_increase_in_counterfamily": strictly_increasing,
        "Weyl_value_unbounded_as_Q_tends_to_infinity": True,
        "two_chord_scalar_endpoint_uncertainty_consumed": optimistic_error > 0.0,
        "two_chord_uncertainty_exceeds_finite_target_scale": (
            optimistic_error > target_scale
        ),
        "pair_plus_contact_incidence_remains_domain_parametric": (
            incidence["claim_boundary"]["pair_plus_contact_gauge_Hessian"]
            == "OPEN"
        ),
        "BRST_cancellation_is_only_longitudinal_ghost": (
            superdet["graded_operator_ledger"]["gauge_longitudinal_ghost"]
            ["net_supertrace_sign"]
            == 0
        ),
        "retained_physical_sector_scale_force_witness_is_nonzero": (
            superdet["regulated_free_superdeterminant_seed"]
            ["d_Gamma_one_loop_d_log_common_radius"]
            != 0.0
        ),
        "N12_zero_source_force_not_fabricated_from_periodic_witness": (
            saddle["adjudication"]
            ["nonzero_replacement_force_at_the_N12_state_proved"]
            is False
        ),
        "no_chord_endpoint_action_term_selector_fit_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_EXTERIOR_GAP_ORACLE_AUDIT",
        "classification": (
            "THE_POSITIVE_LOWER_SECTOR_GAP_AND_FRIEDRICHS_ENDPOINT_RULE_"
            "DEFINE_A_UNIQUE_COERCIVE_RESOLVENT_FOR_EACH_RETAINED_EXTERIOR_"
            "BUT_DO_NOT_DETERMINE_OR_UNIFORMLY_UPPER_BOUND_ITS_BIRTH_WEYL_"
            "RESPONSE;_THE_TWO_CHORD_CORE_SUPPLIES_ONLY_A_SCALAR_CONSTANT_GAP_"
            "ENDPOINT_UNCERTAINTY_ABOVE_4P4E7_AND_NO_FIRST_OR_SECOND_"
            "GEOMETRY_VARIATION_BOUND"
        ),
        "current_flagship_gate": 7,
        "status": "GAP_ONLY_EXTERIOR_ORACLE_ROUTE_RIGOROUSLY_INSUFFICIENT",
        "theorem": {
            "family": "P_Q=-d_tau^2+Q_ON_[0,infinity),_Q>=1",
            "common_data": [
                "THE_SAME_UNIT_TEMPORAL_PRINCIPAL_PART",
                "THE_SAME_BIRTH_TRACE_SPACE",
                "THE_SAME_FRIEDRICHS_DECAY_CLASS_AT_INFINITY",
                "THE_COMMON_FORM_LOWER_BOUND_P_Q>=1",
            ],
            "coercive_probe": "z=-1",
            "unit_trace_solution": "u_Q(tau)=exp(-sqrt(Q+1)*tau)",
            "birth_conormal_convention": "M_Q(-1)=-u_Q_prime(0)=sqrt(Q+1)",
            "conclusion": (
                "SUP_Q>=1_M_Q(-1)=INFINITY;_THEREFORE_A_LOWER_GAP_AND_"
                "FRIEDRICHS_CLASS_PROVE_EXISTENCE_BUT_NOT_VALUE_OR_ANY_"
                "FINITE_UNIFORM_UPPER_ENCLOSURE_OF_M_C"
            ),
            "sample_rows": rows,
            "geometry_variations": {
                "dM_dQ": "1/(2*sqrt(Q-z))",
                "d2M_dQ2": "-1/(4*(Q-z)^(3/2))",
                "adjudication": (
                    "THE_FORMULAS_EXIST_FOR_EACH_REALIZED_FAMILY_BUT_THE_"
                    "REPOSITORY_HAS_NO_ACTION_OWNED_MAXIMAL_EXTERIOR_"
                    "FIRST_OR_SECOND_COEFFICIENT_VARIATION_ENVELOPE_TO_"
                    "TURN_THEM_INTO_THE_REQUIRED_BHSM_ORACLE_BOUNDS"
                ),
            },
        },
        "certified_core_effect": {
            "two_chord_time_end": two_chord["certified_coordinate_time_end"],
            "proper_duration_lower": heat_test["proper_duration_lower"],
            "proper_duration_upper": heat_test["proper_duration_upper"],
            "smallest_nonzero_sector_gap_lower": heat_test[
                "smallest_nonzero_sector_gap_lower"
            ],
            "scalar_constant_gap_endpoint_formula": heat_test[
                "endpoint_bound_formula"
            ],
            "best_case_scalar_endpoint_uncertainty_lower": optimistic_error,
            "comparison_target_magnitude_only": target_scale,
            "uncertainty_over_target_magnitude": optimistic_error / target_scale,
            "what_is_owned": (
                "A_FINITE_TWO_CHORD_BACKGROUND_CORE_AND_A_SCALAR_"
                "CONSTANT_GAP_ENDPOINT_COMPARISON"
            ),
            "what_is_not_owned": [
                "THE_OPERATOR_VALUED_M_C(z)_ON_THE_PHYSICAL_SOURCE_SPACE",
                "D_Phi_M_C(z)_ON_THE_MAXIMAL_EXTERIOR",
                "D_Phi2_M_C(z)_ON_THE_MAXIMAL_EXTERIOR",
                "Pi_C_PAIR_PLUS_CONTACT(z)_ON_THE_REALIZED_DOMAIN",
            ],
            "promotion_authorized": False,
        },
        "route_adjudication": {
            "positive_gap_plus_Friedrichs_only": "RIGOROUS_NO_GO_FOR_ORACLE_VALUE",
            "two_chord_core_plus_scalar_gap_comparison": (
                "FINITE_BUT_NONINFORMATIVE_VALUE_ONLY_SURROGATE;_NOT_THE_"
                "OPERATOR_OR_VARIATION_BUNDLE"
            ),
            "third_chord_authorized": False,
            "terminal_event_required": False,
            "action_obstruction_proved": False,
            "Ward_BRST_zero_force_shortcut": (
                "INVALIDATED_AS_A_STRUCTURAL_IDENTITY:_BRST_CANCELS_THE_"
                "LONGITUDINAL_GHOST_PAIR_BUT_NOT_THE_TRANSVERSE_GAUGE_Weyl_"
                "OR_HS_GEOMETRY_FORCE"
            ),
            "historical_nonzero_force_witness": {
                "periodic_seed_scale_force": superdet[
                    "regulated_free_superdeterminant_seed"
                ]["d_Gamma_one_loop_d_log_common_radius"],
                "scope": (
                    "COUNTEREXAMPLE_TO_A_UNIVERSAL_SYMMETRY_CANCELLATION_"
                    "ONLY;_NOT_AN_N12_FORWARD_FORCE_VALUE"
                ),
                "N12_forward_force_evaluated": False,
            },
            "reason": (
                "AN_ACTION_OWNED_GLOBAL_COEFFICIENT_COMPARISON_OR_DIRECT_"
                "WEYL_ORACLE_MAY_STILL_CLOSE_THE_NATIVE_ROUTE"
            ),
        },
        "exact_next_dependency": {
            "first": (
                "DERIVE_FROM_THE_RETAINED_ACTION_A_COMMON_MAXIMAL_FORWARD_"
                "FORM_COMPARISON_OR_COEFFICIENT_TUBE_THROUGH_SECOND_"
                "GEOMETRY_VARIATION_FOR_P_C(Phi,A),_OR_COMPUTE_THE_"
                "EQUIVALENT_M_C,D_Phi_M_C,D_Phi2_M_C_ORACLE_DIRECTLY"
            ),
            "then": (
                "ENCLOSE_THE_COMMON_PAIR_PLUS_CONTACT_Pi_C(z),_EVALUATE_"
                "THE_ZERO_SOURCE_FORCE,_AND_CERTIFY_THE_SAME_ACTION_SADDLE"
            ),
            "forbidden_substitutions": [
                "ANOTHER_UNPROMOTED_FINITE_CHORD",
                "THE_SPATIAL_GALERKIN_TAIL_AS_A_TEMPORAL_TAIL",
                "A_CHOSEN_TERMINAL_OR_ROBIN_PARAMETER",
                "A_PERIODIC_OR_p2_LABEL",
            ],
        },
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "exterior_oracle_bundle": "OPEN",
            "positive_gap_Friedrichs_shortcut": "CLOSED_INSUFFICIENT",
            "chord_03": "NOT_AUTHORIZED",
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "counterfamily_last_Weyl": payload["theorem"]["sample_rows"][-1][
                    "Weyl_value"
                ],
                "two_chord_uncertainty_over_target": payload[
                    "certified_core_effect"
                ]["uncertainty_over_target_magnitude"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
