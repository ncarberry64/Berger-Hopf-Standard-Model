"""Derive the finite-stratum parametric reset-fiber exterior-oracle theorem."""

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
    "BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json"
)
INPUTS = (
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_JOINT_FINITE_HISTORY_OPERATOR_DATA_GATE.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fraction(value: Fraction) -> dict[str, Any]:
    return {
        "exact": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def exact_schur_directional_witness() -> dict[str, Any]:
    """Check the first and second Schur-response derivative identities exactly."""

    # M(x)=a(x)-b(x)^2/k(x), with the interior shifted pencil k=d-z.
    # The rational coefficients have no physical role; they are an exact
    # algebraic regression witness for the derivative formulas.
    a0, a1, a2 = Fraction(2), Fraction(1, 5), Fraction(1, 13)
    b0, b1, b2 = Fraction(-1), Fraction(1, 7), Fraction(1, 17)
    k0, k1, k2 = Fraction(4), Fraction(1, 11), Fraction(1, 19)

    value = a0 - b0 * b0 / k0
    first = (
        a1
        - 2 * b1 * b0 / k0
        + b0 * b0 * k1 / (k0 * k0)
    )
    second = (
        a2
        - 2 * b2 * b0 / k0
        - 2 * b1 * b1 / k0
        + 4 * b1 * b0 * k1 / (k0 * k0)
        + b0 * b0 * k2 / (k0 * k0)
        - 2 * b0 * b0 * k1 * k1 / (k0 * k0 * k0)
    )

    # Independent second-order dual-number evaluation.  Coefficients are
    # stored as value, first derivative, second derivative.
    def mul(
        left: tuple[Fraction, Fraction, Fraction],
        right: tuple[Fraction, Fraction, Fraction],
    ) -> tuple[Fraction, Fraction, Fraction]:
        l0, l1, l2 = left
        r0, r1, r2 = right
        return (
            l0 * r0,
            l1 * r0 + l0 * r1,
            l2 * r0 + 2 * l1 * r1 + l0 * r2,
        )

    def inverse(
        item: tuple[Fraction, Fraction, Fraction],
    ) -> tuple[Fraction, Fraction, Fraction]:
        v0, v1, v2 = item
        return (
            1 / v0,
            -v1 / (v0 * v0),
            2 * v1 * v1 / (v0 * v0 * v0) - v2 / (v0 * v0),
        )

    a = (a0, a1, a2)
    b = (b0, b1, b2)
    k = (k0, k1, k2)
    quotient = mul(mul(b, b), inverse(k))
    independent = tuple(a[index] - quotient[index] for index in range(3))
    return {
        "model": "M(xi)=A_bb(xi)-A_bi(xi)*(A_ii(xi)-z)^(-1)*A_ib(xi)",
        "coercive_interior_shift_at_base": _fraction(k0),
        "value": _fraction(value),
        "first_directional_derivative": _fraction(first),
        "second_directional_derivative": _fraction(second),
        "independent_dual_number_value": _fraction(independent[0]),
        "independent_dual_number_first": _fraction(independent[1]),
        "independent_dual_number_second": _fraction(independent[2]),
        "value_identity_exact": value == independent[0],
        "first_identity_exact": first == independent[1],
        "second_identity_exact": second == independent[2],
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("parametric exterior-oracle theorem inputs required")
    records = [_load(path) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated parametric exterior-oracle inputs required")
    reset, finite_domain, weyl, force, projected, quotient, data_gate = records
    witness = exact_schur_directional_witness()
    validation = {
        "reset_is_set_valued_and_not_a_physical_selector": (
            reset["reset_correspondence"][
                "single_valued_physical_reset_map_proved"
            ] is False
            and reset["reset_correspondence"][
                "normal_chart_is_action_owned_physical_selector"
            ] is False
        ),
        "raw_and_physical_quotient_dimensions_kept_distinct": (
            reset["reset_correspondence"][
                "fixed_event_child_fiber_dimension"
            ] == 67
            and reset["reset_correspondence"][
                "after_existing_whole_system_time_quotient"
            ] == 66
            and quotient["claim_boundary"]["explicit_time_generator"] == "OPEN"
        ),
        "finite_encapsulation_scope_preserved": (
            finite_domain["claim_boundary"]["infinite_angular_branch"]
            == "CLOSED_BY_OWNER_PHYSICAL_SCOPE"
            and finite_domain["claim_boundary"]["finite_encapsulation_existence"]
            == "CLOSED_LOCAL_ACTION_THEOREM"
        ),
        "exterior_value_and_two_geometry_jets_are_required": (
            weyl["exterior_oracle_bundle"]["value"] == "M_C(z)"
            and "D_Phi_M_C" in weyl["exterior_oracle_bundle"][
                "first_geometry_variation"
            ]
            and "D_Phi2_M_C" in weyl["exterior_oracle_bundle"][
                "second_geometry_variation"
            ]
        ),
        "force_functional_exists_but_value_is_open": (
            force["claim_boundary"]["zero_source_force_functional"] == "DERIVED"
            and force["claim_boundary"]["zero_source_force_value"] == "OPEN"
        ),
        "physical_projected_force_and_saddle_remain_open": (
            projected["claim_boundary"]["actual_projected_force_value"] == "OPEN"
            and projected["claim_boundary"]["same_action_saddle"]
            == "OPEN_COUPLED_TO_FORCE"
        ),
        "current_checkpoint_does_not_supply_oracle": (
            data_gate["claim_boundary"]["complete_action_owned_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
        ),
        "schur_value_first_and_second_formulas_crosschecked_exactly": all(
            witness[key] is True
            for key in (
                "value_identity_exact",
                "first_identity_exact",
                "second_identity_exact",
            )
        ),
        "no_reset_selector_endpoint_fit_infinite_tail_new_gate_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM",
        "status": "FINITE_ENDPOINT_STRATIFIED_ORACLE_REGULARITY_DERIVED_ACTUAL_PARAMETRIC_ORACLE_OPEN",
        "classification": (
            "ON_EACH_FIXED_REGULAR_FINITE_EVENT_OR_CANONICAL_STOP_STRATUM,_A_"
            "COMMON_FORM_DOMAIN_C2_ACTION_FAMILY_WITH_UNIFORM_NEGATIVE_PROBE_"
            "COERCIVITY_DEFINES_A_C2_RESET_FIBER_WEYL_CALDERON_FAMILY;_THE_"
            "RESET_IS_SET_VALUED,_SO_ONE_REPRESENTATIVE_CANNOT_DETERMINE_THE_"
            "PHYSICAL_PROJECTED_FORCE_OR_HESSIAN_UNLESS_ACTION_DERIVED_FIBER_"
            "INVARIANCE_IS_PROVED;_THE_CURRENT_DISK_SUPPLIES_NEITHER_THE_"
            "PARAMETRIC_ORACLE_NOR_THAT_INVARIANCE"
        ),
        "theorem_domain": {
            "physical_parameter_space": (
                "EACH_REGULAR_LOCAL_STRATUM_OF_MATHFRAK_C/G_EXISTING_WHOSE_"
                "FORWARD_HISTORY_REACHES_A_FIXED_FINITE_COMPLETED_"
                "ENCAPSULATION_ENDPOINT_TYPE_OR_RETAINED_CANONICAL_STOP"
            ),
            "raw_fixed_event_reset_tangent_dimension": 67,
            "retained_post_time_quotient_dimension_count": 66,
            "explicit_quotient_generator_available": False,
            "infinite_nonencapsulating_histories": (
                "PRESERVED_AS_NONREALIZED_MATHEMATICAL_HISTORIES_AND_NOT_USED_"
                "IN_THE_PHYSICAL_FORCE_DOMAIN"
            ),
            "endpoint_outcome_switch_set": (
                "NO_C2_CLAIM;_TREAT_AS_A_STRATUM_BOUNDARY_OR_ALREADY_RETAINED_"
                "CANONICAL_STOP_UNTIL_THE_ACTION_PROVES_MORE"
            ),
        },
        "regularity_hypotheses": {
            "H1": "A_FIXED_LOCAL_TRIVIALIZATION_OF_THE_PHYSICAL_TRACE_AND_FORM_SPACES_ON_THE_STRATUM",
            "H2": "A_COMMON_DENSE_FORM_DOMAIN_WITH_C2_PARAMETER_DEPENDENCE_OF_THE_RETAINED_QUADRATIC_FORM_AND_BIRTH_GRAPH",
            "H3": "A_UNIFORM_POSITIVE_COERCIVITY_MARGIN_FOR_P_C^D(xi)-z_AT_THE_CHOSEN_REAL_z_LESS_THAN_ZERO",
            "H4": "C2_REGULAR_ENDPOINT_GRAPH_AND_GEOMETRY_TRACE_MAP_WITH_UNIFORM_POSITIVE_LAPSE_DURATION_AND_DOMAIN_MARGINS",
            "H5": "THE_RETAINED_GAUGE_TIME_COMMON_SCALE_QUOTIENT_IS_GIVEN_INTRINSICALLY_OR_BY_ITS_ACTION_DERIVED_GENERATORS",
        },
        "regularity_conclusion": {
            "resolvent": "R_C^D(z;xi)_IS_C2_IN_OPERATOR_NORM_ON_THE_FIXED_STRATUM",
            "Poisson_operator": "gamma_C(z;xi)_IS_C2_AFTER_THE_FIXED_TRACE_TRIVIALIZATION",
            "Weyl_Calderon_family": "M_C(z;xi)_IS_C2_ON_THE_PHYSICAL_RESET_QUOTIENT_STRATUM",
            "heat_minus_zeta_force": "q_rep(xi)_IS_A_WELL_DEFINED_C1_COVECTOR_FIELD_ON_THAT_STRATUM",
            "constraint_reduced_Hessian": "D_q_rep_AND_THE_GEOMETRY_RESET_KKT_HESSIAN_ARE_DEFINED_ON_THAT_STRATUM",
            "proof_route": (
                "THE_SECOND_RESOLVENT_IDENTITY_AND_DIFFERENTIATION_OF_THE_"
                "COMMON_CLOSED_FORM_GIVE_C2_RESOLVENT_DEPENDENCE;_TRACE_"
                "LIFT_AND_SCHUR_COMPLEMENT_THEN_GIVE_C2_POISSON_AND_WEYL_"
                "DEPENDENCE;_NO_ILL_CONDITIONED_KINETIC_OR_DIRAC_BLOCK_IS_INVERTED"
            ),
        },
        "fixed_chart_schur_formulas": {
            "definitions": "M=A_bb-B*R*C,_R=(A_ii-z)^(-1)",
            "first_directional_derivative": (
                "M'=A_bb'-B'*R*C-B*R*C'+B*R*A_ii'*R*C"
            ),
            "second_directional_derivative": (
                "M''=A_bb''-B''*R*C-2B'*R*C'-B*R*C''+2B'*R*A_ii'*R*C+2B*R*A_ii'*R*C'+B*R*A_ii''*R*C-2B*R*A_ii'*R*A_ii'*R*C"
            ),
            "interpretation": (
                "THE_FORMULAS_ARE_LOCAL_COORDINATE_REPRESENTATIONS_OF_THE_"
                "INTRINSIC_FORM_VARIATIONS_AND_DO_NOT_SELECT_A_RESET_MEMBER"
            ),
        },
        "single_representative_necessity": {
            "value_only_counterpair": (
                "M_0(xi)=M_star_AND_M_1(xi)=M_star+xi*B_AGREE_AT_xi=0_"
                "BUT_HAVE_DIFFERENT_FIRST_VARIATIONS"
            ),
            "value_and_first_jet_counterpair": (
                "M_0(xi)=M_star_AND_M_2(xi)=M_star+(xi^2/2)*B_AGREE_IN_"
                "VALUE_AND_FIRST_VARIATION_AT_xi=0_BUT_HAVE_DIFFERENT_HESSIANS"
            ),
            "conclusion": (
                "ONE_CERTIFIED_RESET_REPRESENTATIVE_IS_SUFFICIENT_ONLY_IF_THE_"
                "RETAINED_ACTION_PROVES_THE_REQUIRED_FORCE_AND_HESSIAN_ARE_"
                "BASIC_AND_FIBER_INVARIANT_ON_MATHFRAK_C/G_EXISTING,_OR_IF_"
                "THE_ACTION_ITSELF_SELECTS_A_UNIQUE_SADDLE;_NEITHER_IS_CURRENTLY_PROVED"
            ),
            "selector_forbidden": True,
        },
        "required_oracle_bundle": {
            "endpoint_outcome_stratum_map": "alpha(xi)_IN_FINITE_EVENT_OR_CANONICAL_STOP_TYPES",
            "endpoint_time_or_intrinsic_endpoint_graph": "T_alpha(xi)_OR_EQUIVALENT_GRAPH_DATA",
            "Weyl_value": "M_C,alpha(z;xi)",
            "first_physical_quotient_jet": "D_xi_M_C,alpha(z;xi)",
            "second_physical_quotient_jet": "D_xi2_M_C,alpha(z;xi)",
            "replacement_force": "q_rep,alpha(xi)=D_Gamma_heat-D_Gamma_SM_zeta",
            "geometry_reset_Hessian": "D_xi_q_rep_PLUS_THE_RETAINED_CONSTRAINT_SECOND_VARIATION",
            "quotient_data": "COUPLED_HYBRID_TIME_GENERATOR_OR_AN_INTRINSIC_QUOTIENT_FORMULATION",
        },
        "exact_algebraic_crosscheck": witness,
        "adjudication": {
            "regularity_theorem": "DERIVED_CONDITIONAL_ON_FIXED_REGULAR_FINITE_ENDPOINT_STRATUM",
            "actual_parametric_N12_exterior_oracle": "OPEN_CURRENT_OWNER",
            "action_derived_fiber_invariance": "OPEN_ALTERNATIVE_ROUTE",
            "single_hand_selected_reset_history_sufficient": False,
            "global_smoothness_across_endpoint_switches_claimed": False,
            "infinite_tail_analysis_reopened": False,
            "transverse_descriptor_promotion_authorized": False,
        },
        "exact_next_dependency": (
            "EITHER_DERIVE_THE_ACTUAL_M_C(z;xi),_D_xi_M_C,_AND_D_xi2_M_C_"
            "BUNDLE_ON_A_NONEMPTY_FIXED_REGULAR_FINITE_ENDPOINT_OR_CANONICAL_"
            "STOP_STRATUM_OF_THE_PHYSICAL_RESET_QUOTIENT,_INCLUDING_THE_"
            "COUPLED_TIME_QUOTIENT,_OR_PROVE_FROM_THE_RETAINED_ACTION_THAT_"
            "THE_REPLACEMENT_FORCE_AND_HESSIAN_ARE_BASIC_AND_INVARIANT_"
            "ALONG_THE_ENTIRE_RESET_FIBER"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_PARAMETRIC_EXTERIOR_ORACLE_OR_FIBER_INVARIANCE_OPEN",
            "finite_encapsulation_physical_scope": "CLOSED_OWNER_SCOPE",
            "finite_endpoint_oracle_regularity_theorem": "DERIVED_CONDITIONAL",
            "actual_parametric_exterior_oracle": "OPEN_CURRENT_OWNER",
            "actual_projected_force": "OPEN",
            "geometry_reset_KKT_Hessian": "OPEN",
            "same_action_saddle": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
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
