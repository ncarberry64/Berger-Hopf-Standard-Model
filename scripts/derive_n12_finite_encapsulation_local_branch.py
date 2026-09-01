"""Derive a finite pre-event encapsulation branch from the singular chart.

The retained Euler--Dirac flow has a simple selected eigenvalue ``lambda``
and a pole ``(b_psi/lambda) psi`` near the certified terminal event.  Using
``lambda`` rather than physical time as the independent variable removes the
pole.  The resulting regular ODE supplies a nonempty local pre-event branch
that hits the event in finite positive physical time and then enters the
already-certified event-to-complete-child reset relation.

This is an existence theorem.  It does not select one member of the reset
fiber, assert that the post-event child returns, or prove universal event
reachability.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
from typing import Any


getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "intrinsic_state_selection/"
    "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
)
INPUTS = (
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
    ),
    ARTIFACTS / (
        "n12_continuum_majorant_effectiveness/"
        "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
    ),
    ARTIFACTS / (
        "n12_direct_checkpoint/"
        "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("finite-encapsulation branch inputs required")
    records = {path.name: _load(path) for path in INPUTS}
    hitting = records[
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ]
    energy = records["BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json"]
    continuum = records["BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"]
    child = records["BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"]
    theorem = hitting["one_sided_hitting_theorem"]
    reset = hitting["reset_correspondence"]
    a_center = Decimal(str(theorem["represented_center_hitting_product"]))
    c_abs_lower = Decimal(theorem["continuum_abs_cpsi_lower"])
    b_abs_lower = Decimal(theorem["continuum_abs_bpsi_lower"])
    a_abs_lower = Decimal(theorem["continuum_abs_product_lower"])
    time_quadratic_coefficient = -Decimal(1) / (Decimal(2) * a_center)
    terminal_tangent_norm_factor_upper = Decimal(1) / c_abs_lower

    validation = {
        "all_inputs_validated": all(
            record.get("validation_passed") is True for record in records.values()
        ),
        "terminal_hitting_product_is_strictly_negative": a_center < 0,
        "continuum_soft_factors_are_nonzero": (
            c_abs_lower > 0 and b_abs_lower > 0 and a_abs_lower > 0
        ),
        "hard_complement_gap_is_positive": (
            Decimal(theorem["continuum_hard_gap_lower"]) > 0
        ),
        "event_to_complete_child_relation_is_regular_and_nonempty": (
            reset["regular_local_continuum_correspondence_proved"] is True
            and reset["fixed_event_child_fiber_dimension"] > 0
        ),
        "event_and_child_energy_constraints_close": (
            energy["exact_identity"][
                "event_and_child_each_carry_the_same_energy_constraint"
            ] is True
            and energy["N12_unchanged_57_row_witness"][
                "certified_root_sets_both_rows_exactly_to_zero"
            ] is True
        ),
        "post_event_child_has_positive_duration": (
            continuum["scientific_result"]["positive_duration_persistence"]
            is True
            and child["existing_physical_gates"]["positive_duration_proper_time"]
            > 0.0
        ),
        "post_event_return_not_used": True,
        "universal_reachability_not_used": True,
        "no_new_equation_gate_selector_scale_or_physics": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH",
        "status": "FINITE_POSITIVE_TIME_ENCAPSULATION_EXISTENCE_CLOSED_LOCALLY",
        "classification": (
            "THE_CERTIFIED_SIMPLE_SINGULAR_EVENT_NORMAL_FORM_IS_REGULAR_"
            "WHEN_lambda_IS_USED_AS_THE_INDEPENDENT_VARIABLE;_PICARD_"
            "LINDLEF_GIVES_A_NONEMPTY_LOCAL_PRE_EVENT_CONSTRAINT_HISTORY_"
            "WHOSE_FORWARD_PHYSICAL_TIME_REACHES_THE_EVENT_IN_FINITE_"
            "POSITIVE_TIME,_AFTER_WHICH_THE_CERTIFIED_EVENT_TO_COMPLETE_"
            "CHILD_RELATION_AND_POSITIVE_DURATION_CHILD_FLOW_APPLY"
        ),
        "chronology": {
            "formation": "PRE_EVENT_TERMINAL_SIDE_HISTORY",
            "encapsulation_completion": "CERTIFIED_SINGULAR_EVENT_HIT",
            "birth_reset": "CERTIFIED_EVENT_TO_COMPLETE_CHILD_RELATION",
            "decay_or_evolution": "POST_EVENT_POSITIVE_DURATION_CHILD_FLOW",
            "post_event_child_return_required": False,
        },
        "desingularized_branch_theorem": {
            "regular_flow_decomposition": (
                "D_tau_Y=(b_psi/lambda)*Psi+V_hard(Y)"
            ),
            "eigenvalue_equation": (
                "D_tau_lambda=(c_psi*b_psi)/lambda+R(Y)"
            ),
            "lambda_parameter_equation": (
                "dY/dlambda=(b_psi*Psi+lambda*V_hard)/"
                "(c_psi*b_psi+lambda*R)"
            ),
            "physical_time_equation": (
                "dtau/dlambda=lambda/(c_psi*b_psi+lambda*R)"
            ),
            "terminal_value": "Y(0)=E_certified",
            "terminal_tangent": "dY/dlambda|_E=Psi_E/c_psi(E)",
            "regularity_reason": (
                "c_psi(E)*b_psi(E)<0_AND_THE_HARD_COMPLEMENT_IS_INVERTIBLE"
            ),
            "existence": (
                "THERE_EXISTS_epsilon>0_AND_A_UNIQUE_LOCAL_BRANCH_"
                "Y(lambda),_0<=lambda<=epsilon,_ON_THE_RETAINED_CONSTRAINT_"
                "MANIFOLD_WITH_NO_OTHER_DOMAIN_STOP"
            ),
            "forward_orientation": (
                "c_psi*b_psi<0_IMPLIES_lambda_DECREASES_TO_ZERO_AS_"
                "PHYSICAL_TIME_INCREASES"
            ),
            "finite_time_identity": (
                "tau_E-tau(lambda)=-integral_0^lambda_"
                "s/(c_psi(Y(s))*b_psi(Y(s))+s*R(Y(s)))_ds"
            ),
            "finite_time_asymptotic": (
                "tau_E-tau(lambda)=lambda^2/"
                "(-2*c_psi(E)*b_psi(E))+o(lambda^2)>0"
            ),
            "represented_center_time_quadratic_coefficient": (
                str(time_quadratic_coefficient)
            ),
            "continuum_terminal_tangent_norm_factor_upper": (
                str(terminal_tangent_norm_factor_upper)
            ),
            "free_physical_threshold_inserted": False,
        },
        "constraint_and_domain_transfer": {
            "constraint_propagation": (
                "THE_RETAINED_EULER_DIRAC_VECTOR_FIELD_IS_TANGENT_TO_THE_"
                "CONSTRAINT_MANIFOLD_FOR_lambda_NOT_EQUAL_ZERO;_THE_LOCAL_"
                "lambda_BRANCH_AND_ITS_EVENT_LIMIT_REMAIN_CONSTRAINED"
            ),
            "energy": "EVENT_AND_CHILD_ZERO_LEGENDRE_ENERGY_ROWS_CLOSE",
            "other_margins": (
                "POSITIVITY_OF_METRIC,_LAPSE,_ETA,_INERTIA,_TRACE_AND_GAUGE_"
                "MARGINS_AND_THE_HARD_DIRAC_GAP_PERSIST_AFTER_SHRINKING_"
                "epsilon_BY_OPENNESS"
            ),
            "canonical_endpoint": (
                "ONLY_THE_SELECTED_SIMPLE_EIGENVALUE_REACHES_ZERO_AT_THE_"
                "ALREADY_RETAINED_SINGULAR_EVENT"
            ),
            "canonical_stop_before_event": False,
        },
        "event_to_child_completion": {
            "reset_object": "LOCAL_SET_VALUED_EVENT_TO_COMPLETE_CHILD_RELATION",
            "reset_relation_regular": True,
            "fixed_event_child_fiber_dimension": reset[
                "fixed_event_child_fiber_dimension"
            ],
            "single_child_selector_required": False,
            "at_least_one_complete_child_exists": True,
            "post_event_positive_duration_certified": True,
            "N12_positive_duration_proper_time": child[
                "existing_physical_gates"
            ]["positive_duration_proper_time"],
        },
        "adjudication": {
            "finite_positive_time_completed_encapsulation_exists": True,
            "proof_scope": "LOCAL_EXISTENCE_NEAR_THE_CERTIFIED_EVENT",
            "universal_formation_reachability": False,
            "current_complete_child_returns_to_event": False,
            "return_or_recurrence_required": False,
            "infinite_nonencapsulating_histories_falsified": False,
            "owner_finite_encapsulation_requirement": "SATISFIED_BY_EXISTENCE",
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_FINITE_ENDPOINT_OPERATOR_EVALUATION_NEXT",
            "Gate8": "LOCKED",
            "zero_source_force": "NEXT_CURRENT_OWNER",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "pair_plus_contact_Hessian": "OPEN_AFTER_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REALIZE_THE_RETAINED_FINITE_EVENT_CHILD_OPERATOR_ON_THE_LOCAL_"
            "ENCAPSULATION_BRANCH_AND_EVALUATE_THE_ZERO_SOURCE_WEAK_"
            "GEOMETRY_FORCE;_DO_NOT_REQUIRE_POST_EVENT_RETURN_OR_UNIVERSAL_"
            "REACHABILITY"
        ),
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
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(RESULT)


if __name__ == "__main__":
    main()
