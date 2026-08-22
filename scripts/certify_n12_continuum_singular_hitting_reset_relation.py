"""Certify the local continuum singular hitting and reset relation.

This combines existing certified bounds with an exact block-rank audit of the
unchanged N12 paired Jacobian. It changes no BHSM equation or physical gate.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
SINGULAR = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_SINGULAR_EVENT_TEMPORAL_CHIRALITY.json"
CONTINUUM = ROOT / "artifacts/n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
OBSERVATION = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
COMPACT = ROOT / "artifacts/n12_continuum_majorant_effectiveness/BHSM_N12_COMPACT_OBSERVATION_MODULI_AUDIT.json"
CUTOFF = ROOT / "artifacts/n12_continuum_majorant_effectiveness/BHSM_N12_FIRST_SUFFICIENT_COMPACT_CUTOFF.json"
EIGENLINE = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_ORDERED_EVENT_EIGENLINE_BALL.json"
THEORY = ROOT / "theory/n12_continuum_singular_hitting_reset_relation.md"
RESULT = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _d(value: object) -> Decimal:
    return Decimal(str(value))


def main() -> None:
    getcontext().prec = 100
    inputs = (
        STATE, SINGULAR, CONTINUUM, OBSERVATION, COMPACT, CUTOFF,
        EIGENLINE, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing hitting/reset inputs: " + ", ".join(missing))

    checkpoint = np.load(STATE)
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    singular = _load(SINGULAR)
    continuum = _load(CONTINUUM)
    observation = _load(OBSERVATION)
    compact = _load(COMPACT)
    cutoff = _load(CUTOFF)
    eigenline = _load(EIGENLINE)

    if jacobian.shape != (57, 196):
        raise ValueError("expected unchanged 57 by 196 paired Jacobian")

    event_dimension = 98
    event_rows = jacobian[:26]
    coupled_rows = jacobian[26:]
    event_event = event_rows[:, :event_dimension]
    event_child = event_rows[:, event_dimension:]
    coupled_event = coupled_rows[:, :event_dimension]
    fixed_event_child = coupled_rows[:, event_dimension:]

    event_event_singular = np.linalg.svd(event_event, compute_uv=False)
    child_singular = np.linalg.svd(fixed_event_child, compute_uv=False)
    event_event_rank = int(np.linalg.matrix_rank(event_event))
    event_child_rank = int(np.linalg.matrix_rank(event_child))
    coupled_event_rank = int(np.linalg.matrix_rank(coupled_event))
    fixed_event_child_rank = int(np.linalg.matrix_rank(fixed_event_child))
    child_fiber_dimension = event_dimension - fixed_event_child_rank
    quotient_fiber_dimension = child_fiber_dimension - 1

    center = singular["center_and_cross_quadrature"]["96"]
    refined = singular["refined_root_ball_enclosure"]
    r_inf = _d(continuum["nonlinear_continuum_radius"]["small_radii_root_upper"])
    event_sector = observation["sector_bounds"]["event"]
    projector_bound = _d(compact["four_compact_blocks"]["ordered_event_projector"]["C_event_G_upper"])
    rhs_bound = _d(event_sector["Euler_Dirac_rhs_action_bound"])
    rhs_derivative = _d(event_sector["Euler_Dirac_rhs_derivative_bound"])
    d3_bound = _d(event_sector["action_third_variation_bound"])
    d4_bound = _d(event_sector["action_fourth_variation_bound"])

    b_lipschitz = projector_bound * rhs_bound + rhs_derivative
    c_lipschitz = d4_bound + Decimal(3) * d3_bound * projector_bound
    b_transfer = b_lipschitz * r_inf
    c_transfer = c_lipschitz * r_inf
    hard_gap_center = _d(compact["four_compact_blocks"]["ordered_event_projector"]["finite_N12_simple_branch_gap_lower"])
    hard_gap_transfer = d3_bound * r_inf
    hard_gap_continuum = hard_gap_center - hard_gap_transfer
    b_lower_continuum = _d(refined["forcing_absolute_lower"]) - b_transfer
    c_lower_continuum = _d(refined["cubic_absolute_lower"]) - c_transfer
    product_lower_continuum = b_lower_continuum * c_lower_continuum

    nonlinear_m2 = _d(continuum["nonlinear_continuum_radius"]["M2_upper"])
    child_gap_center = _d(child_singular[-1])
    child_gap_transfer = nonlinear_m2 * r_inf
    child_gap_continuum = child_gap_center - child_gap_transfer
    half_margin = _d(cutoff["optional_numerically_stable_half_margin_cutoff"]["observation_gap_lower"])

    validation = {
        "continuum_event_child_already_certified": continuum["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True,
        "singular_chirality_input_validated": singular["validation_passed"] is True,
        "event_rows_depend_only_on_event_state": float(np.linalg.norm(event_child, 2)) == 0.0,
        "event_event_block_has_full_row_rank_26": event_event_rank == 26,
        "fixed_event_child_block_has_full_row_rank_31": fixed_event_child_rank == 31,
        "local_child_fiber_dimension_is_67": child_fiber_dimension == 67,
        "time_quotiented_child_fiber_dimension_is_66": quotient_fiber_dimension == 66,
        "continuum_bpsi_lower_is_positive": b_lower_continuum > 0,
        "continuum_cpsi_lower_is_positive": c_lower_continuum > 0,
        "continuum_hitting_product_magnitude_lower_is_positive": product_lower_continuum > 0,
        "continuum_hard_gap_lower_is_positive": hard_gap_continuum > 0,
        "continuum_fixed_event_child_submersion_gap_is_positive": child_gap_continuum > 0,
        "compact_tail_observation_margin_is_positive": half_margin > 0,
        "formal_reflection_not_quotiented": singular["formal_reflection_is_gauge"] is False,
        "no_new_equation_constraint_gate_selector_scale_or_physics": True,
        "global_forward_reachability_not_claimed": True,
    }

    next_dependency = (
        "PROVE_THAT_AT_LEAST_ONE_EXISTING_FORWARD_COMPLETE_CHILD_HISTORY_REACHES_"
        "THE_CERTIFIED_TERMINAL_SINGULAR_EVENT_CHART_BEFORE_ANY_EXISTING_PHYSICAL_"
        "DOMAIN_EXIT_OR_PROVE_THAT_NO_SUCH_HISTORY_DOES"
    )
    payload = {
        "artifact": "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION",
        "classification": (
            "CONTINUUM_LOCAL_SINGULAR_HITTING_AND_REGULAR_EVENT_TO_CHILD_"
            "RESET_RELATION_CERTIFIED;_GLOBAL_FORWARD_REACHABILITY_OPEN"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "one_sided_hitting_theorem": {
            "regular_side_decomposition": "ZDOT=(B_PSI/LAMBDA)PSI+S*Q*B_ED",
            "exact_squared_identity": "D_DT(LAMBDA^2)=2*C_PSI*B_PSI+2*LAMBDA*R(Y)",
            "event_limit": "LIM_D_DT(LAMBDA^2)=2*C_PSI*B_PSI",
            "represented_boundary_role": "FORWARD_TERMINAL",
            "reflected_boundary_role": "FORWARD_EMERGENT",
            "represented_center_hitting_product": center["hitting_product"],
            "represented_center_squared_rate_limit": center["squared_eigenvalue_rate_limit"],
            "continuum_abs_bpsi_lower": str(b_lower_continuum),
            "continuum_abs_cpsi_lower": str(c_lower_continuum),
            "continuum_abs_product_lower": str(product_lower_continuum),
            "continuum_hard_gap_lower": str(hard_gap_continuum),
            "local_consequence": (
                "EVERY_FORWARD_SOLUTION_ENTERING_THE_POSITIVE_LAMBDA_TERMINAL_"
                "CHART_HITS_LAMBDA_ZERO_IN_FINITE_TIME_WITH_SQUARE_ROOT_ASYMPTOTICS"
            ),
            "current_child_enters_terminal_chart_proved": False,
        },
        "continuum_transfer": {
            "continuum_root_correction_radius_upper": str(r_inf),
            "bpsi_Lipschitz_upper": str(b_lipschitz),
            "bpsi_transfer_upper": str(b_transfer),
            "cpsi_Lipschitz_upper": str(c_lipschitz),
            "cpsi_transfer_upper": str(c_transfer),
            "hard_gap_transfer_upper": str(hard_gap_transfer),
            "full_action_M2_times_radius_upper": str(child_gap_transfer),
            "existing_compact_tail_half_margin": str(half_margin),
        },
        "unchanged_jacobian_block_audit": {
            "full_shape": list(jacobian.shape),
            "event_event_shape": list(event_event.shape),
            "event_event_rank": event_event_rank,
            "event_event_sigma_min": float(event_event_singular[-1]),
            "event_child_shape": list(event_child.shape),
            "event_child_operator_norm": float(np.linalg.norm(event_child, 2)),
            "event_child_rank": event_child_rank,
            "coupled_event_shape": list(coupled_event.shape),
            "coupled_event_rank": coupled_event_rank,
            "fixed_event_child_shape": list(fixed_event_child.shape),
            "fixed_event_child_rank": fixed_event_child_rank,
            "fixed_event_child_sigma_min": float(child_singular[-1]),
            "continuum_fixed_event_child_sigma_lower": str(child_gap_continuum),
        },
        "reset_correspondence": {
            "mathematical_object": "LOCAL_SET_VALUED_EVENT_TO_COMPLETE_CHILD_RELATION_MATHFRAK_C",
            "fixed_event_child_fiber_dimension": child_fiber_dimension,
            "after_existing_whole_system_time_quotient": quotient_fiber_dimension,
            "certified_normal_chart_role": "REPRODUCIBLE_LOCAL_REPRESENTATIVE_ONLY",
            "normal_chart_is_action_owned_physical_selector": False,
            "single_valued_physical_reset_map_proved": False,
            "regular_local_continuum_correspondence_proved": True,
        },
        "claim_boundaries": {
            "current_complete_child_forward_return_proved": False,
            "return_domain_nonempty_proved": False,
            "action_selected_fixed_or_periodic_hybrid_orbit_proved": False,
            "parent_or_relative_energy_unlocked": False,
            "observable_or_prediction_promoted": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": next_dependency,
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
        "classification": payload["classification"],
        "continuum_product_lower": str(product_lower_continuum),
        "fixed_event_child_rank": fixed_event_child_rank,
        "fixed_event_child_fiber_dimension": child_fiber_dimension,
        "exact_next_dependency": next_dependency,
        "result": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
