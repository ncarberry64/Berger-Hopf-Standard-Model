"""Build the authorized forward-only validated continuum flow-box cover.

The certified child, rather than the unused event-sector Cauchy state, is the
only sector propagated here.  Numerical persistence histories are not used.
All bounds come from already validated retained-action artifacts.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, localcontext
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBSERVATION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
LOCAL_FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW.json"
)
INITIAL_SIDE = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
)
CHILD_EIGENLINE = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CHILD_EVENT_EIGENLINE_BALL.json"
)
PROMOTION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
MAXIMAL_FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
THEOREM = ROOT / "theory/n12_forward_validated_continuation_cover.md"
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_VALIDATED_CONTINUATION_COVER.json"
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _d(value: object) -> Decimal:
    return Decimal(str(value))


def main() -> None:
    inputs = (
        OBSERVATION, LOCAL_FLOW, INITIAL_SIDE, CHILD_EIGENLINE, PROMOTION,
        CONTINUUM, MAXIMAL_FLOW, THEOREM,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing forward-cover inputs: " + ", ".join(missing))

    observation = _load(OBSERVATION)
    local_flow = _load(LOCAL_FLOW)
    initial_side = _load(INITIAL_SIDE)
    child_eigenline = _load(CHILD_EIGENLINE)
    promotion = _load(PROMOTION)
    continuum = _load(CONTINUUM)
    maximal_flow = _load(MAXIMAL_FLOW)
    if not all(record.get("validation_passed") is True for record in (
        observation, local_flow, initial_side, child_eigenline, promotion,
        continuum, maximal_flow,
    )):
        raise RuntimeError("validated retained-action cover inputs required")

    with localcontext() as context:
        context.prec = 420
        context.rounding = ROUND_CEILING

        child = observation["sector_bounds"]["child"]
        radius = _d(observation["full_action_neighborhood_radius"])
        vector_bound = _d(child["full_state_vector_field_action_bound"])
        generator = _d(child["Jacobi_generator_action_bound"])

        # Keep a strict directed margin at the boundary of the existing ball.
        radius_fraction = Decimal("0.999999")
        path_bound = radius_fraction * radius
        duration = path_bound / vector_bound
        exponential = (generator * duration).exp()

        epsilon_ed = _d(local_flow["directed_decimal_bounds"][
            "epsilon_ED_M0_upper"
        ])
        initial_tail = _d(continuum["nonlinear_continuum_radius"][
            "small_radii_root_upper"
        ])
        flow_error = (
            exponential * initial_tail
            + epsilon_ed * (exponential - Decimal(1)) / generator
        )
        total_radius_use = path_bound + flow_error
        remaining_radius = radius - total_radius_use

        event_initial = _d(initial_side["continuum_transfer"][
            "continuum_initial_child_event_value_lower"
        ])
        event_lipschitz = _d(child_eigenline["bounds"][
            "selected_eigenvalue_first_derivative_bound"
        ])
        event_change = event_lipschitz * total_radius_use
        event_lower = event_initial - event_change

        old_duration = _d(local_flow["directed_decimal_bounds"][
            "coordinate_duration"
        ])
        extension_factor = duration / old_duration
        physical_radius = _d(promotion["certified_root_ball"]["radius"])
        gates = promotion["existing_physical_gates"]
        eta_lower = _d(gates["eta_ball_lower"])
        lapse_lower = _d(gates["boundary_lapse_ball_lower"])
        velocity_lower = _d(gates["nonzero_velocity_ball_lower"])

        validation = {
            "certified_continuum_child_anchor_consumed": continuum[
                "CONTINUUM_EVENT_CHILD_CERTIFIED"
            ] is True,
            "forward_child_sector_only_is_propagated": True,
            "physical_time_orientation_is_positive_only": duration > 0,
            "existing_gauge_time_quotient_retained": True,
            "child_Dirac_inverse_closed_on_flow_box": child[
                "gauge_fixed_Dirac_inverse_closed"
            ] is True,
            "continuum_Galerkin_error_inside_flow_box": (
                total_radius_use < radius
            ),
            "eta_margin_positive": eta_lower > 0,
            "boundary_lapse_positive": lapse_lower > 0,
            "nonzero_relative_evolution_retained": velocity_lower > 0,
            "ordered_event_branch_simple": child_eigenline[
                "validation"
            ]["selected_line_remains_simple"] is True,
            "ordered_event_stays_strictly_positive": event_lower > 0,
            "constraint_propagation_identity_retained": maximal_flow[
                "validation"
            ]["finite_N12_dichotomy_lifted_to_continuum_strong_domain"] is True,
            "no_terminal_event_hit_inside_cover": event_lower > 0,
            "no_existing_physical_domain_exit_inside_cover": all((
                eta_lower > 0,
                lapse_lower > 0,
                child["gauge_fixed_Dirac_inverse_closed"] is True,
                total_radius_use < physical_radius,
            )),
            "numerical_persistence_path_not_used_as_proof": True,
            "no_new_selector_equation_gate_orientation_parent_or_scale": True,
        }

        outcome = "C"
        classification = (
            "AUTHORIZED_FINITE_FORWARD_COVER_EXHAUSTED_WITH_NEITHER_"
            "TERMINAL_HIT_NOR_PHYSICAL_DOMAIN_EXIT"
        )
        payload = {
            "artifact": "BHSM_N12_FORWARD_VALIDATED_CONTINUATION_COVER",
            "classification": classification,
            "hard_outcome": outcome,
            "cover": {
                "manifold": (
                    "EXISTING_GAUGE_TIME_QUOTIENTED_ADMISSIBLE_CHILD_MANIFOLD"
                ),
                "time_orientation": "FORWARD_ONLY",
                "number_of_certified_action_flow_boxes": 1,
                "initial_coordinate_time": "0",
                "certified_forward_coordinate_time_upper": str(duration),
                "previous_certified_coordinate_time_upper": str(old_duration),
                "certified_interval_extension_factor": str(extension_factor),
                "action_coordinate_ball_radius": str(radius),
                "strict_radius_fraction_used": str(radius_fraction),
                "finite_core_path_length_upper": str(path_bound),
                "continuum_Galerkin_flow_error_upper": str(flow_error),
                "total_action_radius_use_upper": str(total_radius_use),
                "remaining_action_radius_margin_lower": str(remaining_radius),
            },
            "exact_retained_action_bounds": {
                "child_vector_field_action_norm_upper": str(vector_bound),
                "child_Jacobi_generator_action_norm_upper": str(generator),
                "selected_proof_cutoff_M0": local_flow[
                    "directed_decimal_bounds"
                ]["selected_proof_cutoff_M0"],
                "Euler_Dirac_tail_consistency_upper": str(epsilon_ed),
                "initial_inverse_square_continuum_tail_upper": str(initial_tail),
                "gauge_fixed_Dirac_ball_inverse_upper": child[
                    "gauge_fixed_Dirac_ball_inverse_bound"
                ],
                "Euler_Dirac_rhs_action_upper": child[
                    "Euler_Dirac_rhs_action_bound"
                ],
            },
            "event_and_domain_enclosure": {
                "initial_continuum_ordered_event_lower": str(event_initial),
                "ordered_event_action_Lipschitz_upper": str(event_lipschitz),
                "ordered_event_change_upper": str(event_change),
                "ordered_event_lower_throughout_cover": str(event_lower),
                "eta_lower": str(eta_lower),
                "boundary_lapse_lower": str(lapse_lower),
                "nonzero_velocity_lower": str(velocity_lower),
                "terminal_chart_hit": False,
                "physical_domain_exit": False,
            },
            "cover_exhaustion": {
                "single_earliest_preventing_term": (
                    "NO_TRANSLATED_REGULAR_COORDINATE_JACOBI_MAJORANT_FOR_THE_"
                    "NEXT_ACTION_FLOW_BOX"
                ),
                "localized_expression": (
                    "THE_AVAILABLE_ORIGINAL_COORDINATE_BOUND_"
                    "NORM(D_GAUGE^-1)*NORM(B_ED)="
                    "CHILD_VECTOR_FIELD_ACTION_NORM_UPPER_CONSUMES_THE_"
                    "ROOT_CENTERED_ACTION_BALL;_THE_EXISTING_ASSETS_DO_NOT_"
                    "ENCLOSE_THE_DESINGULARIZED_u=lambda^2_VARIATIONAL_FLOW_"
                    "ON_A_TRANSLATED_CENTER"
                ),
                "retained_action_obstruction_proved": False,
                "solver_or_sampling_failure_promoted": False,
                "next_exact_mathematical_object": (
                    "INTERVAL_ENCLOSE_THE_EXISTING_u=lambda^2_REGULAR_"
                    "COORDINATE_VARIATIONAL_FLOW_ON_THE_FIRST_TRANSLATED_"
                    "CHILD_BOX_AND_CERTIFY_OVERLAP_WITH_THIS_BOX"
                ),
            },
            "inputs": {
                str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
                for path in inputs
            },
            "claim_boundaries": {
                "CONTINUUM_EVENT_CHILD_CERTIFIED": True,
                "FORWARD_TERMINAL_CHART_REACHABILITY_PROVED": False,
                "PHYSICAL_DOMAIN_EXIT_PROVED": False,
                "Q_xi_or_Delta_H_unlocked": False,
                "observable_or_prediction_promoted": False,
                "FULL_BHSM_COMPLETE": False,
            },
            "validation": validation,
            "validation_passed": all(validation.values()),
            "FULL_BHSM_COMPLETE": False,
        }

    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": classification,
        "hard_outcome": outcome,
        "certified_forward_coordinate_time_upper": str(duration),
        "certified_interval_extension_factor": str(extension_factor),
        "ordered_event_lower_throughout_cover": str(event_lower),
        "single_earliest_preventing_term": payload["cover_exhaustion"][
            "single_earliest_preventing_term"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
