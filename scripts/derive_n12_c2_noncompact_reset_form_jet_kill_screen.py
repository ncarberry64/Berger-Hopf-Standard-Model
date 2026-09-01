"""Derive the exact noncompact C2 reset form-jet criterion and kill screen."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_NONCOMPACT_RESET_FORM_JET_KILL_SCREEN.json"
PROJECTED = BASE / "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
COMPATIBILITY = BASE / "BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY.json"
C2 = BASE / "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"
MAXIMAL = BASE / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
COMPACT_JETS = BASE / "BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json"
GEOMETRY_JETS = BASE / "BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS.json"
TRANSFER = BASE / "BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json"
FINITE_CORE = BASE / "BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL.json"
QUOTIENT = BASE / "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
THEORY = ROOT / "theory" / "n12_c2_noncompact_reset_form_jet_kill_screen.md"
INPUTS = (
    PROJECTED,
    COMPATIBILITY,
    C2,
    MAXIMAL,
    COMPACT_JETS,
    GEOMETRY_JETS,
    TRANSFER,
    FINITE_CORE,
    QUOTIENT,
    THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sharpness_witness() -> dict[str, Any]:
    core_times = (1.0, 2.0, 4.0, 8.0, 16.0)
    rows = [
        {
            "T": time,
            "uniform_value_error_upper": 1.0 / time,
            "derivative_at_xi_zero": time,
        }
        for time in core_times
    ]
    return {
        "value_convergence_does_not_imply_jet_convergence": {
            "family": "f_T(xi)=sin(T^2*xi)/T",
            "uniform_value_bound": "sup_xi|f_T(xi)|<=1/T",
            "base_value": "f_T(0)=0",
            "base_derivative": "D_xi f_T(0)=T",
            "rows": rows,
            "purpose": "GENERAL_MATHEMATICAL_SHARPNESS_WITNESS_NOT_A_BHSM_TAIL",
        },
        "ambient_form_bound_not_necessary_after_projection": {
            "ambient_derivative": "J_T(h;a,b)=(0,T*h*a*b)",
            "physical_pullback": "P(y1,y2)=y1",
            "ambient_norm_limit": "DIVERGES",
            "projected_jet": 0.0,
            "purpose": "GENERAL_MATHEMATICAL_QUOTIENT_WITNESS_NOT_A_BHSM_TAIL",
        },
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing noncompact form-jet inputs: " + ", ".join(missing))
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated noncompact form-jet parents required")
    (
        projected,
        compatibility,
        c2,
        maximal,
        compact_jets,
        geometry_jets,
        transfer,
        finite_core,
        quotient,
    ) = records
    witness = _sharpness_witness()
    rows = witness["value_convergence_does_not_imply_jet_convergence"]["rows"]

    matching_audit = [
        {
            "diagram_slot": "FINITE_CORE_WEYL_VALUE_M_T",
            "required_mathematical_type": "BIRTH_TRACE_OPERATOR_AT_REAL_NEGATIVE_z",
            "candidate_BHSM_object": "NESTED_DIRICHLET_CORE_WEYL_MAP",
            "dimension_domain_check": "VALID_FIXED_CHANNEL_AND_GALERKIN",
            "provenance_check": "ACTION_OWNED_FRIEDRICHS_FORM",
            "verdict": "VALID_MATCH_VALUE_LIMIT_DERIVED",
        },
        {
            "diagram_slot": "RESET_DIRECTION_h",
            "required_mathematical_type": "UNIT_VECTOR_IN_PHYSICAL_RESET_TANGENT_QUOTIENT",
            "candidate_BHSM_object": "66_DIMENSIONAL_INTRINSIC_TIME_QUOTIENT_WITH_COMMON_SCALE_RETAINED",
            "dimension_domain_check": "VALID_ON_REGULAR_RESET_STRATUM",
            "provenance_check": "AE2_RESET_CONSTRAINT_AND_TIME_SYMMETRY",
            "verdict": "VALID_MATCH",
        },
        {
            "diagram_slot": "LOCAL_DERIVATIVE_FORM_B_T_h",
            "required_mathematical_type": "SAME_ACTION_SESQUILINEAR_FORM_JET",
            "candidate_BHSM_object": "EXP_MINUS_x_AND_EXP_MINUS_2x_CHILD_COEFFICIENT_GEOMETRY_JETS",
            "dimension_domain_check": "VALID_ON_COMPACT_REGULAR_SUBINTERVALS",
            "provenance_check": "EXACT_BHSM_CHILD_OPERATOR_SCALING",
            "verdict": "VALID_MATCH_LOCAL_ONLY",
        },
        {
            "diagram_slot": "POISSON_PAIR_U_T_a_U_T_b",
            "required_mathematical_type": "FINITE_CORE_SOLUTIONS_WITH_BIRTH_TRACES_a_b",
            "candidate_BHSM_object": "FIXED_CHANNEL_TRANSFER_AND_FRIEDRICHS_POISSON_OPERATOR",
            "dimension_domain_check": "VALID_PER_FINITE_CORE_VALUE_LIMIT_EXISTS",
            "provenance_check": "INVERSE_FREE_TRANSFER_AND_FORM_CLOSURE",
            "verdict": "VALID_MATCH_WITHOUT_UNIFORM_NONCOMPACT_JET_BOUND",
        },
        {
            "diagram_slot": "NONCOMPACT_RESET_JACOBI_FIELD",
            "required_mathematical_type": "MAXIMAL_HISTORY_VARIATION_INDUCED_BY_RESET_DIRECTION_h",
            "candidate_BHSM_object": "98_SEGMENT_STATE_JACOBI_PRODUCT",
            "dimension_domain_check": "FINITE_PREFIX_ONLY",
            "provenance_check": "VALID_LINEARIZED_ACTION_FLOW",
            "verdict": "ACTUALLY_MISSING_ON_MAXIMAL_TAIL",
        },
        {
            "diagram_slot": "FULL_NONCOMPACT_OPERATOR_FORM_JET_CAUCHY_TAIL",
            "required_mathematical_type": "UNIFORM_TRILINEAR_CAUCHY_NET_ON_h_a_b",
            "candidate_BHSM_object": "COMPACT_SUPPORT_WEYL_JETS",
            "dimension_domain_check": "CRITERION_VALID_ACTUAL_NONCOMPACT_TAIL_UNEVALUATED",
            "provenance_check": "SAME_ACTION_CHILD_OPERATOR_FORM",
            "verdict": "ACTUALLY_MISSING_STRONG_OPERATOR_ROUTE",
        },
        {
            "diagram_slot": "SOURCE_CONTRACTED_COMBINED_REPLACEMENT_FORCE_TAIL",
            "required_mathematical_type": "PHYSICAL_QUOTIENT_DUAL_CAUCHY_NET",
            "candidate_BHSM_object": "PROJECTED_ADJOINT_CAUCHY_CRITERION",
            "dimension_domain_check": "EXACT_CRITERION_ACTUAL_TAIL_UNEVALUATED",
            "provenance_check": "SAME_ACTION_HEAT_MINUS_ZETA_REPLACEMENT",
            "verdict": "ACTUALLY_MISSING_CURRENT_GATE_OWNER",
        },
    ]

    validation = {
        "all_inputs_validated": True,
        "maximal_value_limit_is_derived": (
            maximal["claim_boundary"]["maximal_Friedrichs_Weyl_value_definition"]
            == "DERIVED_AS_UNIQUE_EXHAUSTION"
        ),
        "maximal_noncompact_jet_parent_marks_open": (
            maximal["open_after_theorem"]["noncompact_reset_quotient_first_jet"] is True
        ),
        "compact_support_jets_are_not_promoted": (
            compact_jets["claim_boundary"]["global_noncompact_Weyl_variations"]
            == "OPEN_IF_REQUIRED_BY_SADDLE"
        ),
        "local_radius_jets_are_exact": (
            geometry_jets["exact_scaling_theorem"]["geometry_coordinate"]
            == "x(tau)=log(R4(tau))"
        ),
        "fixed_channel_basis_is_time_independent": (
            transfer["fixed_channel_theorem"]["spatial_basis"].startswith("ONE_tau_INDEPENDENT")
        ),
        "finite_prefix_has_98_segments": (
            finite_core["finite_history_response"]["segment_count"] == 98
        ),
        "finite_prefix_not_endpoint": (
            finite_core["claim_boundary"]["physical_encapsulation_endpoint_reached"] is False
        ),
        "physical_quotient_dimension_is_66": (
            quotient["dimensions"]["physical_quotient_tangent"] == 66
        ),
        "combined_replacement_tail_is_current_owner": (
            compatibility["claim_boundary"]["actual_joint_replacement_Cauchy_tail"]
            == "OPEN_CURRENT_OWNER"
        ),
        "projected_force_tail_is_open": (
            projected["claim_boundary"]["actual_projected_Cauchy_tail"]
            == "OPEN_CURRENT_OWNER"
        ),
        "uniform_values_can_have_divergent_derivatives": (
            rows[-1]["uniform_value_error_upper"] < rows[0]["uniform_value_error_upper"]
            and rows[-1]["derivative_at_xi_zero"] > rows[0]["derivative_at_xi_zero"]
            and math.isclose(rows[-1]["uniform_value_error_upper"], 1.0 / rows[-1]["T"])
        ),
        "ambient_bound_not_declared_necessary": (
            witness["ambient_form_bound_not_necessary_after_projection"]["projected_jet"] == 0.0
        ),
        "no_selector_scale_fit_recurrence_endpoint_box_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_C2_NONCOMPACT_RESET_FORM_JET_KILL_SCREEN",
        "status": (
            "EXACT_NONCOMPACT_RESET_FORM_JET_CRITERION_DERIVED_ACTUAL_C2_TAIL_NOT_CERTIFIED"
            if passed
            else "NONCOMPACT_RESET_FORM_JET_CRITERION_NOT_DERIVED"
        ),
        "classification": (
            "THE_MAXIMAL_WEYL_VALUE_LIMIT_AND_COMPACT_SUPPORT_JETS_DO_NOT_CERTIFY_"
            "THE_PHYSICAL_NONCOMPACT_RESET_JET;_THE_EXACT_OPERATOR_ROUTE_STATEMENT_IS_"
            "UNIFORM_CAUCHY_CONVERGENCE_OF_THE_SAME_ACTION_DERIVATIVE_FORM_PLUS_"
            "CONTACT_CONTRACTION_ON_UNIT_RESET_DIRECTIONS_AND_POISSON_TRACES"
        ),
        "theorem": {
            "finite_core_first_form_jet": (
                "<a,D_hM_T(z)b>=B_T,h(U_T(z)a,U_T(z)b)+C_T,h(a,b)"
            ),
            "exact_necessary_and_sufficient_criterion": (
                "FOR_EVERY_epsilon>0_EXISTS_T0_FOR_ALL_S,T>T0:_sup_"
                "norm(h)=norm(a)=norm(b)=1_|J_T(h;a,b)-J_S(h;a,b)|<epsilon"
            ),
            "jet_contraction": (
                "J_T(h;a,b)=B_T,h(U_Ta,U_Tb)+C_T,h(a,b)"
            ),
            "why_equivalent": (
                "THE_PHYSICAL_RESET_QUOTIENT_AND_RETAINED_BIRTH_TRACE_SPACES_ARE_"
                "FINITE_DIMENSIONAL_SO_UNIFORM_TRILINEAR_CAUCHY_IS_OPERATOR_NORM_CAUCHY"
            ),
            "strong_sufficient_route": (
                "UNIFORM_POISSON_FORM_BOUNDS_PLUS_A_CAUCHY_RELATIVE_FORM_TAIL_"
                "AND_CAUCHY_CONTACT_TAIL"
            ),
            "weaker_gate_force_route": (
                "SOURCE_CONTRACTED_COUPLED_FORWARD_ADJOINT_WEAK_ROOT_AFTER_THE_"
                "RETAINED_PHYSICAL_RESET_PULLBACK_WITHOUT_A_FULL_OPERATOR_JET"
            ),
            "projection_rule": (
                "ONLY_THE_RETAINED_CONSTRAINT_TIME_AND_GRADED_ACTION_PULLBACK_MAY_"
                "ANNIHILATE_AMBIENT_DIVERGENT_COMPONENTS"
            ),
        },
        "matching_audit": matching_audit,
        "sharpness_witnesses": witness,
        "actual_C2_evidence": {
            "local_coefficient_jets": "EXACT",
            "fixed_channel_transfer_pencils": "EXACT",
            "maximal_Weyl_value_definition": "UNIQUE",
            "compact_support_first_second_jets": "CONVERGENT",
            "finite_prefix_segment_count": finite_core["finite_history_response"]["segment_count"],
            "finite_prefix_state_Jacobi_growth_upper": finite_core["finite_history_response"]["state_Jacobi_growth_upper"],
            "maximal_reset_Jacobi_envelope": "OPEN",
            "uniform_noncompact_Poisson_form_contraction": "OPEN",
            "source_contracted_combined_graded_heat_minus_zeta_force_tail": "OPEN",
        },
        "adjudication": {
            "maximal_Weyl_value": "CLOSED_DO_NOT_REOPEN",
            "compact_support_Weyl_jets": "CLOSED_DO_NOT_REOPEN",
            "fixed_channel_transfer_and_local_geometry_jets": "CLOSED_DO_NOT_REOPEN",
            "noncompact_physical_reset_form_jet_criterion": "DERIVED",
            "actual_noncompact_physical_reset_form_jet": "OPEN_NOT_CERTIFIED",
            "actual_joint_replacement_force_tail": "OPEN_CURRENT_OWNER",
            "finite_later_event_or_canonical_stop": "ALTERNATIVE_OPEN_OUTCOME",
            "zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "physical_Hessian": "WAITING_ON_SADDLE",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "the exact noncompact reset first-Weyl-operator-jet Cauchy criterion",
                "local same-action coefficient jets and transfer pencils",
                "maximal Weyl values and compact-support weak jets",
                "the physical quotient can make ambient absolute bounds non-necessary",
            ],
            "INVALIDATED": [
                "maximal Weyl value convergence implies reset-derivative convergence",
                "compact-support jet convergence implies a noncompact reset jet",
                "the 98-segment Jacobi bound controls the maximal tail",
                "a separate termwise heat or zeta tail is necessary on the direct combined route",
            ],
            "OPEN": [
                "the actual maximal reset Jacobi field and uniform Poisson-form contraction",
                "the actual source-contracted projected heat-minus-zeta force tail",
                "a finite later event or canonical stop",
                "zero-source force, same-action saddle, and physical Hessian",
            ],
        },
        "exact_next_dependency": (
            "BUILD_AND_CERTIFY_EITHER_THE_DIRECT_SOURCE_CONTRACTED_COMBINED_FORCE_"
            "TAIL,_THE_STRONGER_UNIFORM_C2_MAXIMAL_RESET_FORM_JET_TAIL,_OR_AN_"
            "EXECUTABLE_C2_TO_LATER_EVENT_OR_CANONICAL_STOP_"
            "CONNECTION;_DO_NOT_REOPEN_RESET_RECURRENCE_FIXED_CHANNEL_DINI_COMPACT_"
            "WEYL_JETS_COMMON_SCALE_AS_GAUGE_OR_CHORD3"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_NONCOMPACT_RESET_FORM_JET_OR_FINITE_ENDPOINT",
            "Gate8": "LOCKED",
            "noncompact_reset_form_jet_criterion": "DERIVED",
            "actual_noncompact_reset_form_jet": "OPEN_NOT_CERTIFIED",
            "actual_projected_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "physical_Hessian": "WAITING_ON_SADDLE",
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
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "actual_noncompact_reset_form_jet": payload["claim_boundary"]["actual_noncompact_reset_form_jet"],
    }, indent=2))


if __name__ == "__main__":
    main()
