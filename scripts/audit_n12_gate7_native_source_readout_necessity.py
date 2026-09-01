"""Audit the native Gate-7 source-readout dependencies.

This audit does not change Gate 7.  It separates the retained-action source
Hessian from the optional terminal-return route and checks whether the
inherited ``partial_(p^2)`` readout is executable on the corrected forward
domain.  Two exact finite-dimensional witnesses record the logical gaps:

* a derivative at ``p^2`` is not fixed without an operator/source family;
* a compactly supported response still depends on the exterior through the
  Schur-complement (Weyl/Calderon) response.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT.json"
)
INPUTS = (
    ARTIFACTS / "BHSM_aether_unified_m5_m4_pushforward_v15_69.json",
    ARTIFACTS / "BHSM_aether_cycle_dtn_local_limit_v15_90.json",
    ARTIFACTS / "BHSM_aether_common_quantum_superdeterminant_v15_96.json",
    ARTIFACTS / "BHSM_aether_common_source_frechet_response_v15_99.json",
    ARTIFACTS / "BHSM_frozen_prediction_dependency_graph_v6_30_8.json",
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_FORWARD_REACHABLE_COMPONENT_THEOREM_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_GATE7_TWO_CHORD_INTERVAL_SIGN_STOP.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _fraction_payload(value: Fraction) -> dict[str, object]:
    return {
        "exact": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def _operator_family_witness() -> dict[str, object]:
    """Show that a base quadratic form does not determine its p^2 derivative."""

    base = Fraction(3, 1)
    operator_derivatives = (Fraction(0, 1), Fraction(1, 1))
    source_derivatives = (Fraction(0, 1), Fraction(1, 1))
    return {
        "base_parameter": "lambda=p^2/mu_star^2-1",
        "same_base_operator": "K_c(0)=3",
        "operator_families": [
            {
                "family": f"K_{index}(lambda)=3+{slope}*lambda",
                "derivative_at_zero": _fraction_payload(slope),
            }
            for index, slope in enumerate(operator_derivatives)
        ],
        "same_base_source": "a_c(0)=1",
        "source_families_with_fixed_K": [
            {
                "family": f"a_{index}(lambda)=1+{slope}*lambda",
                "derivative_of_3*a_c(lambda)^2_at_zero": _fraction_payload(
                    6 * slope
                ),
            }
            for index, slope in enumerate(source_derivatives)
        ],
        "conclusion": (
            "THE_VALUE_AT_ONE_PARAMETER_POINT_DOES_NOT_DETERMINE_THE_"
            "PARAMETER_DERIVATIVE;_THE_RETAINED_FORWARD_ACTION_MUST_OWN_"
            "THE_K_A(lambda)_AND_ADMISSIBLE_SOURCE_FAMILY"
        ),
    }


def _exterior_schur_witness() -> dict[str, object]:
    """Show exactly that a core response changes with the exterior block."""

    # P_e = [[2,-1,0],[-1,3,-1],[0,-1,e]].  The first two coordinates
    # are the certified/source core and the last coordinate is the exterior.
    # Schur elimination gives S_e=[[2,-1],[-1,3-1/e]].
    exterior_values = (Fraction(2, 1), Fraction(4, 1))
    responses: list[dict[str, object]] = []
    exact_values: list[Fraction] = []
    for exterior in exterior_values:
        schur_22 = Fraction(3, 1) - Fraction(1, 1) / exterior
        determinant = Fraction(2, 1) * schur_22 - Fraction(1, 1)
        response = schur_22 / determinant
        exact_values.append(response)
        responses.append(
            {
                "exterior_diagonal_e": _fraction_payload(exterior),
                "exterior_Weyl_term": _fraction_payload(
                    Fraction(1, 1) / exterior
                ),
                "core_Schur_22": _fraction_payload(schur_22),
                "core_response_for_source_(1,0)": _fraction_payload(response),
            }
        )
    difference = exact_values[0] - exact_values[1]
    return {
        "positive_operator_family": (
            "P_e=[[2,-1,0],[-1,3,-1],[0,-1,e]],_e_IN_{2,4}"
        ),
        "compressed_resolvent_identity": (
            "Pi_core*(P-z)^(-1)*Pi_core^*="
            "(A-z-B*(C-z)^(-1)*B^*)^(-1)"
        ),
        "rows": responses,
        "exact_response_difference": _fraction_payload(difference),
        "conclusion": (
            "COMPACT_SOURCE_SUPPORT_DOES_NOT_REMOVE_EXTERIOR_DEPENDENCE;_"
            "THE_EXTERIOR_ENTERS_ONLY_THROUGH_ITS_WEYL_CALDERON_RESPONSE"
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all native Gate-7 necessity inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    }
    for name, record in records.items():
        if name == "BHSM_frozen_prediction_dependency_graph_v6_30_8.json":
            if record.get("frozen_prediction_changed") is not False:
                raise RuntimeError("the frozen prediction graph must remain unchanged")
        elif record.get("validation_passed") is not True:
            raise RuntimeError(f"input did not validate: {name}")

    pushforward = records["BHSM_aether_unified_m5_m4_pushforward_v15_69.json"]
    local_dtn = records["BHSM_aether_cycle_dtn_local_limit_v15_90.json"]
    superdet = records["BHSM_aether_common_quantum_superdeterminant_v15_96.json"]
    source = records["BHSM_aether_common_source_frechet_response_v15_99.json"]
    frozen = records["BHSM_frozen_prediction_dependency_graph_v6_30_8.json"]
    domain = records["BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"]
    reachable = records[
        "BHSM_N12_GATE7_FORWARD_REACHABLE_COMPONENT_THEOREM_AUDIT.json"
    ]
    heat_tail = records["BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"]
    sign_stop = records["BHSM_N12_GATE7_TWO_CHORD_INTERVAL_SIGN_STOP.json"]

    frozen_text = json.dumps(frozen, sort_keys=True).lower()
    reachability_tokens = ("terminal", "reachability", "reset", "gate7")
    frozen_reachability_dependencies = [
        token for token in reachability_tokens if token in frozen_text
    ]

    inherited_formula = pushforward["common_derivative_ledger"][
        "absolute_local_gauge_residue"
    ]
    operator_witness = _operator_family_witness()
    exterior_witness = _exterior_schur_witness()
    endpoint_rule = domain["endpoint_rule"]

    provenance = {
        "inherited_scalar_formula": inherited_formula,
        "formula_origin": "V15_69_FORMAL_M5_TO_M4_BOUNDARY_PUSHFORWARD",
        "first_evaluated_operator_domain": superdet[
            "joint_quantum_derivative_contract"
        ]
        ["graded_cycle_operator"],
        "forward_domain_now_owned": domain["ownership"]
        ["abstract_forward_source_domain_action_owned"],
        "periodic_cycle_restored": domain["ownership"]["periodic_cycle_restored"],
        "dynamic_frequency_response_derived": local_dtn["claim_boundary"]
        ["dynamic_frequency_response_derived"],
        "spatial_derivative_scope": {
            "spatial_Fij": local_dtn["claim_boundary"]
            ["local_spatial_Fij_derivative_coefficient_derived"],
            "Gauss_constraint": local_dtn["claim_boundary"]
            ["local_Gauss_constraint_derivative_coefficient_derived"],
            "Lorentz_Maxwell": local_dtn["claim_boundary"]
            ["Lorentz_invariant_FmunuFmunu_coefficient_derived"],
        },
        "source_vertex_contract_fixed": source["claim_boundary"]
        ["physical_source_vertex_contract_fixed"],
        "radial_angular_vertex_matrices_assembled_in_origin": source[
            "claim_boundary"
        ]["radial_angular_vertex_matrices_assembled"],
    }

    necessity_adjudication = {
        "A_well_defined_reset_only": (
            "INSUFFICIENT_FOR_THE_NUMERICAL_OR_PHYSICAL_GATE7_READOUT"
        ),
        "B_one_terminal_reaching_history": (
            "EXISTENCE_ONLY_SUFFICIENT_ENDPOINT_ROUTE_NOT_NATIVE_NECESSITY"
        ),
        "C_event_or_stop_for_every_history": (
            "NOT_THE_RETAINED_MAXIMAL_FLOW_THEOREM_BECAUSE_AN_INFINITE_"
            "REGULAR_HISTORY_REMAINS_AN_ALLOWED_OUTCOME"
        ),
        "D_universal_terminal_reachability": "NOT_REQUIRED_AND_NOT_DERIVED",
        "exact_native_requirement": (
            "AN_ACTION_OWNED_FORWARD_SPECTRAL_OR_SOURCE_PARAMETER_FAMILY_"
            "AND_A_MAXIMAL_HISTORY_EXTERIOR_WEYL_CALDERON_RESPONSE_OR_"
            "EQUIVALENT_COMPLETE_COEFFICIENT_ORACLE,_FOLLOWED_BY_THE_SAME_"
            "ACTION_SADDLE_AND_PAIR_PLUS_CONTACT_HESSIAN"
        ),
        "terminal_event_role": (
            "ONE_OPTIONAL_FINITE_ENDPOINT_REALIZATION_OF_THE_EXTERIOR_"
            "RESPONSE;_NOT_A_PREREQUISITE_FOR_THE_FRIEDRICHS_INFINITE_OR_"
            "EXCLUDED_ENDPOINT_DOMAIN"
        ),
    }

    readout_adjudication = {
        "current_formula_status": (
            "INHERITED_FORMAL_CONTRACT_NOT_YET_AN_EXECUTABLE_FORWARD_"
            "DOMAIN_EVALUATOR"
        ),
        "why": (
            "THE_FORWARD_LINEAGE_DEFINES_THE_BILINEAR_HESSIAN_FOR_SUPPLIED_"
            "ADMISSIBLE_SOURCES_BUT DOES_NOT CONSTRUCT_K_A(p),_a_i(p),_OR_"
            "THE_MEANING_OF_p2_AFTER_THE_PERIODIC_FOURIER_REALIZATION_IS_"
            "RETIRED"
        ),
        "candidate_meanings": {
            "spatial_coexact_eigenvalue": (
                "DERIVED_ONLY_AS_A_SPATIAL_SUPPORTING_COEFFICIENT_AND_NOT_"
                "A_LORENTZIAN_MAXWELL_RESIDUE"
            ),
            "temporal_frequency": (
                "OPEN_AND_NOT_INHERITABLE_FROM_THE_RETIRED_PERIODIC_CYCLE"
            ),
            "local_microlocal_covector": (
                "NO_ACTION_OWNED_LOW_ENERGY_SOURCE_FAMILY_OR_NORMALIZED_"
                "FORWARD_EVALUATOR_HAS_BEEN_CONSTRUCTED"
            ),
        },
        "definition_must_precede_value_computation": True,
    }

    exact_next_dependency = {
        "first": (
            "CONSTRUCT_FROM_THE_RETAINED_FORWARD_ACTION_AN_ADMISSIBLE_BRST_"
            "TRANSVERSE_ONE_PARAMETER_SOURCE_OR_OPERATOR_FAMILY_WHOSE_"
            "PARAMETER_IS_THE_DECLARED_p2_OVER_mu_star2_AND_PROVE_THE_"
            "PAIR_PLUS_CONTACT_HESSIAN_IS_DIFFERENTIABLE_ALONG_IT"
        ),
        "second": (
            "EVALUATE_OR_ENCLOSE_THE_EXTERIOR_WEYL_CALDERON_RESPONSE_AT_"
            "THE_BOUNDARY_OF_THE_CERTIFIED_SOURCE_CORE;_A_COMPLETE_MAXIMAL_"
            "HISTORY_COEFFICIENT_ORACLE_OR_AN_ACTUAL_FINITE_ENDPOINT_GRAPH_"
            "IS_SUFFICIENT_BUT_NOT_LOGICALLY_NECESSARY"
        ),
        "then": (
            "EVALUATE_THE_ZERO_SOURCE_WEAK_GEOMETRY_FORCE,_CERTIFY_THE_SAME_"
            "ACTION_SADDLE,_AND_COMPUTE_THE_FULL_PAIR_PLUS_CONTACT_RESIDUE_"
            "WITH_WARD_BRST_CONTROL"
        ),
        "chord_03_authorized": False,
    }

    validation = {
        "all_inputs_present_and_validated": True,
        "inherited_p2_formula_traced_to_v15_69": inherited_formula.startswith(
            "Z_g=partial_(p^2)"
        ),
        "first_evaluated_operator_is_periodic": "S1_tau" in provenance[
            "first_evaluated_operator_domain"
        ],
        "periodic_cycle_not_restored": not provenance["periodic_cycle_restored"],
        "dynamic_frequency_response_still_open": not provenance[
            "dynamic_frequency_response_derived"
        ],
        "Lorentz_Maxwell_coefficient_not_derived": not provenance[
            "spatial_derivative_scope"
        ]["Lorentz_Maxwell"],
        "maximal_domain_allows_infinite_Friedrichs_endpoint": (
            "FRIEDRICHS" in endpoint_rule["if_Tmax_is_infinite"]
        ),
        "maximal_domain_allows_finite_exit_Friedrichs_endpoint": (
            "FRIEDRICHS"
            in endpoint_rule["if_finite_strong_blowup_domain_exit_or_Dirac_exit"]
        ),
        "reachable_theorem_retains_infinite_branch": (
            "INFINITE_REGULAR_FORWARD_HISTORY_WITH_EVENT_NONZERO_FOR_ALL_FINITE_TIME"
            in reachable["clause_adjudication"]["6_two_outcome_gate7_dichotomy"]
            ["retained_exhaustive_outcomes"]
        ),
        "two_chord_tail_not_promoted": not heat_tail["adjudication"]
        ["two_chord_finite_core_promotable_to_complete_heat_response"],
        "event_sign_stop_not_promoted_to_action_obstruction": not sign_stop[
            "canonical_blocker"
        ]["retained_action_incompatibility_proved"],
        "operator_family_witness_nonunique": (
            operator_witness["operator_families"][0]["derivative_at_zero"]
            ["exact"]
            != operator_witness["operator_families"][1]["derivative_at_zero"]
            ["exact"]
        ),
        "source_family_witness_nonunique": (
            operator_witness["source_families_with_fixed_K"][0]
            ["derivative_of_3*a_c(lambda)^2_at_zero"]["exact"]
            != operator_witness["source_families_with_fixed_K"][1]
            ["derivative_of_3*a_c(lambda)^2_at_zero"]["exact"]
        ),
        "compact_core_response_depends_on_exterior": (
            exterior_witness["exact_response_difference"]["exact"] == "1/72"
        ),
        "frozen_predictions_have_no_reachability_dependency": not bool(
            frozen_reachability_dependencies
        ),
        "Gate7_status_not_changed": True,
        "Gate8_remains_locked": True,
        "no_chord3_new_action_selector_scale_fit_or_physics": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT",
        "classification": (
            "TERMINAL_EVENT_REACHABILITY_IS_NOT_A_NATIVE_GATE7_SOURCE_"
            "HESSIAN_REQUIREMENT;_THE_FIRST_UNRESOLVED_EXECUTABLE_READOUT_"
            "OBJECT_IS_THE_ACTION_OWNED_FORWARD_p2_SOURCE_OR_OPERATOR_"
            "FAMILY_AND_ITS_EXTERIOR_WEYL_CALDERON_RESPONSE"
        ),
        "current_flagship_gate": 7,
        "status": "NATIVE_DEPENDENCY_LOCALIZED_GATE7_UNCHANGED",
        "provenance": provenance,
        "necessity_adjudication": necessity_adjudication,
        "readout_adjudication": readout_adjudication,
        "exact_witnesses": {
            "parameter_derivative": operator_witness,
            "exterior_Schur_response": exterior_witness,
        },
        "frozen_prediction_audit": {
            "frozen_prediction_changed": frozen["frozen_prediction_changed"],
            "reachability_dependency_tokens_found": frozen_reachability_dependencies,
            "terminal_reachability_is_a_frozen_prediction_dependency": False,
        },
        "downstream": {
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "Gate9_and_later": "LOCKED_BY_GATE7_NOT_BY_TERMINAL_RETURN_DIRECTLY",
            "physical_coupling_value": "NOT_EVALUATED",
        },
        "exact_next_dependency": exact_next_dependency,
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "Gate7_status_changed": False,
        "chord_03_authorized": False,
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
                "classification": payload["classification"],
                "exact_next_dependency": payload["exact_next_dependency"]["first"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
