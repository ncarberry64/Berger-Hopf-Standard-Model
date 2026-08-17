"""Continue the unchanged N5 child map on its 16-row nonflux fiber.

This is proposal geometry only.  Promotion is still decided by the exact
fixed 18-row merit, the retained eta domain, and the existing child gates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _canonical_pair_at_order,
    _child_rows_at_order,
    _eta_legendre_minimum,
    _metric_radial_flux_covector_at_order,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    sobolev_weights,
    spectral_frequencies,
)


def continue_n5_fiber(
    path: Path, *, iterations: int = 8, trust_radius: float = 256.0,
    pair_step: float = 1.0, project_nonflux_first: bool = False,
) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    child = result["N5_event_conditioned_complete_child_reconstruction"]
    order = 5
    points = 44
    size = dimensions(order)
    qdim = size["coordinates"]
    variable_count = 2 * qdim + size["multipliers"]
    nonflux_count = 16
    source = child["child_state"]
    exact_source = source.get("binary64_hex")
    if exact_source is not None:
        source = {
            **source,
            "coordinates": [float.fromhex(item) for item in exact_source["coordinates"]],
            "velocities": [float.fromhex(item) for item in exact_source["velocities"]],
            "multipliers": [float.fromhex(item) for item in exact_source["multipliers"]],
        }
    state = np.concatenate((
        np.asarray(source["coordinates"], dtype=float),
        np.asarray(source["velocities"], dtype=float),
        np.asarray(source["multipliers"], dtype=float),
    ))
    event = next(
        run["event"] for run in result[
            "N5_independent_eta_branch_event_classification"
        ]["quadrature_runs"] if int(run["points"]) == points
    )
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    frequencies = spectral_frequencies(order)
    regularity = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity["velocities"],
        regularity["multipliers"],
    ))
    row_scales = np.asarray(
        child["proposal_model"]["fixed_reference_row_scales"], dtype=float
    )

    def exact_rows(physical: np.ndarray) -> np.ndarray:
        return _child_rows_at_order(
            order, physical, q_event, event_momentum, event_flux,
            points=points, flux_derivative_method="complex_step",
        )

    def nonflux_jacobian(physical: np.ndarray) -> np.ndarray:
        q = physical[:qdim]
        velocity = physical[qdim:2 * qdim]
        multipliers = physical[2 * qdim:]
        jet = exact_full_action_jet_at_state(
            order, q, velocity, multipliers, points=points
        )
        gradient = np.asarray(jet.gradient, dtype=float)
        hessian = np.asarray(jet.hessian, dtype=float)
        multiplier_start = 2 * qdim
        constraint_jacobian = hessian[multiplier_start:, :]
        energy_gradient = np.concatenate((
            velocity @ hessian[qdim:2 * qdim, :qdim] - gradient[:qdim],
            hessian[qdim:2 * qdim, qdim:2 * qdim] @ velocity,
            velocity @ hessian[qdim:2 * qdim, multiplier_start:]
            - gradient[multiplier_start:],
        ))
        matrix = np.empty((nonflux_count, variable_count))
        trace = _trace_jacobian_at_order(order)
        for column in range(variable_count):
            direction = np.zeros(variable_count)
            direction[column] = 1.0 / direction_weights[column]
            matrix[:3, column] = trace @ direction[:qdim]
            matrix[3:13, column] = constraint_jacobian @ direction
            matrix[13, column] = energy_gradient @ direction
            outer = physical.astype(complex) + 1j * 1.0e-20 * direction
            momentum, _, _, _ = _canonical_pair_at_order(
                order, outer[:qdim], outer[qdim:2 * qdim],
                outer[2 * qdim:], points=points,
            )
            matrix[14:16, column] = np.imag(momentum) / 1.0e-20
        return matrix / row_scales[:nonflux_count, None]

    solver_values = state * direction_weights
    rows = exact_rows(state)
    scaled = rows / row_scales
    initial_merit = float(np.linalg.norm(scaled))
    projection_history: list[dict[str, float | bool]] = []
    if project_nonflux_first:
        for projection_iteration in range(24):
            nonflux_norm = float(np.linalg.norm(scaled[:nonflux_count]))
            if nonflux_norm < 1.0e-11:
                break
            jacobian_a = nonflux_jacobian(state)
            correction = np.linalg.lstsq(
                jacobian_a, -scaled[:nonflux_count], rcond=1.0e-12
            )[0]
            correction_norm = float(np.linalg.norm(correction))
            projection_trial = None
            for exponent in range(25):
                factor = 2.0 ** (-exponent)
                trial_values = solver_values + factor * correction
                trial = trial_values / direction_weights
                eta_trial = _eta_legendre_minimum(
                    order, trial[:qdim], trial[2 * qdim:], points=800
                )["minimum"]
                if eta_trial <= 0.0:
                    continue
                try:
                    trial_rows = exact_rows(trial)
                except (
                    ArithmeticError, RuntimeError, ValueError,
                    np.linalg.LinAlgError,
                ):
                    continue
                trial_scaled = trial_rows / row_scales
                trial_nonflux = float(np.linalg.norm(
                    trial_scaled[:nonflux_count]
                ))
                if trial_nonflux < nonflux_norm:
                    projection_trial = (
                        factor, trial_values, trial, trial_rows,
                        trial_scaled, trial_nonflux, eta_trial,
                    )
                    break
            projection_history.append({
                "iteration": projection_iteration,
                "nonflux_norm_before": nonflux_norm,
                "raw_correction_norm": correction_norm,
                "accepted": projection_trial is not None,
            })
            if projection_trial is None:
                break
            (
                factor, solver_values, state, rows, scaled,
                trial_nonflux, eta_trial,
            ) = projection_trial
            projection_history[-1].update({
                "factor": factor,
                "nonflux_norm_after": trial_nonflux,
                "eta_minimum": eta_trial,
            })
    history: list[dict[str, object]] = []
    accepted = 0
    paired_evaluations = 0
    bounded_start = float(np.linalg.norm(solver_values))
    message = "maximum fiber iterations reached"
    for iteration in range(iterations):
        merit = float(np.linalg.norm(scaled))
        if merit < 1.0e-15:
            message = "scaled complete-child merit converged"
            break
        jacobian_a = nonflux_jacobian(state)
        _, singular, vh = np.linalg.svd(jacobian_a, full_matrices=True)
        rank_tolerance = (
            np.finfo(float).eps * max(jacobian_a.shape) * singular[0]
        )
        rank = int(np.count_nonzero(singular > rank_tolerance))
        if rank != nonflux_count:
            message = "nonflux fiber rank lost"
            break
        null_basis = vh[rank:].T
        particular = np.linalg.lstsq(
            jacobian_a, -scaled[:nonflux_count], rcond=1.0e-12
        )[0]
        flux_on_null = np.empty((2, null_basis.shape[1]))
        pair_failed = False
        for column in range(null_basis.shape[1]):
            direction = null_basis[:, column]
            pair_rows = []
            for sign in (-1.0, 1.0):
                trial_values = solver_values + sign * pair_step * direction
                trial = trial_values / direction_weights
                if _eta_legendre_minimum(
                    order, trial[:qdim], trial[2 * qdim:], points=800
                )["minimum"] <= 0.0:
                    pair_failed = True
                    break
                try:
                    pair_rows.append(exact_rows(trial) / row_scales)
                    paired_evaluations += 1
                except (ArithmeticError, RuntimeError, ValueError, np.linalg.LinAlgError):
                    pair_failed = True
                    break
            if pair_failed:
                break
            flux_on_null[:, column] = (
                pair_rows[1][-2:] - pair_rows[0][-2:]
            ) / (2.0 * pair_step)
        if pair_failed:
            message = "admissible paired null-fiber slope unavailable"
            break
        particular_norm = float(np.linalg.norm(particular))
        particular_flux_change = np.zeros(2)
        if particular_norm > 1.0e-14:
            unit_particular = particular / particular_norm
            pair_rows = []
            for sign in (-1.0, 1.0):
                trial = (
                    solver_values + sign * pair_step * unit_particular
                ) / direction_weights
                pair_rows.append(exact_rows(trial) / row_scales)
                paired_evaluations += 1
            particular_flux_change = particular_norm * (
                pair_rows[1][-2:] - pair_rows[0][-2:]
            ) / (2.0 * pair_step)
        null_step = np.linalg.lstsq(
            flux_on_null,
            -scaled[-2:] - particular_flux_change,
            rcond=1.0e-12,
        )[0]
        null_delta = null_basis @ null_step
        forward_coupled = particular + null_delta
        proposal_directions = {
            "coupled_fiber": forward_coupled,
            "nonflux_fiber_projection": particular,
            "tangent_flux": null_delta,
            "reverse_coupled_fiber": -forward_coupled,
            "reverse_nonflux_projection": -particular,
            "reverse_tangent_flux": -null_delta,
        }
        raw_delta_norm = float(np.linalg.norm(
            proposal_directions["coupled_fiber"]
        ))
        accepted_trial = None
        accepted_label = None
        for label, raw_direction in proposal_directions.items():
            direction = raw_direction.copy()
            direction_norm = float(np.linalg.norm(direction))
            if direction_norm > trust_radius:
                direction *= trust_radius / direction_norm
            for exponent in range(17):
                factor = 2.0 ** (-exponent)
                trial_values = solver_values + factor * direction
                trial = trial_values / direction_weights
                eta = _eta_legendre_minimum(
                    order, trial[:qdim], trial[2 * qdim:], points=800
                )["minimum"]
                if eta <= 0.0:
                    continue
                try:
                    trial_rows = exact_rows(trial)
                except (
                    ArithmeticError, RuntimeError, ValueError,
                    np.linalg.LinAlgError,
                ):
                    continue
                trial_scaled = trial_rows / row_scales
                trial_merit = float(np.linalg.norm(trial_scaled))
                if (
                    trial_merit < merit
                    and (
                        accepted_trial is None
                        or trial_merit < accepted_trial[5]
                    )
                ):
                    accepted_trial = (
                        factor, trial_values, trial, trial_rows,
                        trial_scaled, trial_merit, eta,
                    )
                    accepted_label = label
        history.append({
            "iteration": iteration,
            "fiber_rank": rank,
            "fiber_dimension": int(null_basis.shape[1]),
            "minimum_nonflux_singular_value": float(singular[-1]),
            "raw_proposal_norm": raw_delta_norm,
            "raw_particular_norm": particular_norm,
            "raw_null_tangent_norm": float(np.linalg.norm(null_delta)),
            "accepted": accepted_trial is not None,
            "merit_before": merit,
            "solver_state_norm": float(np.linalg.norm(solver_values)),
        })
        if accepted_trial is None:
            message = "paired exact fiber proposal failed exact merit descent"
            break
        factor, solver_values, state, rows, scaled, trial_merit, eta = accepted_trial
        history[-1].update({
            "factor": factor,
            "selected_proposal": accepted_label,
            "merit_after": trial_merit,
            "eta_minimum": eta,
        })
        accepted += 1
    final_rows = exact_rows(state)
    final_merit = float(np.linalg.norm(final_rows / row_scales))
    final_raw_residual_norm = float(np.linalg.norm(final_rows))
    eta = _eta_legendre_minimum(
        order, state[:qdim], state[2 * qdim:], points=5000
    )
    constraint_stop = 14
    root_closed = bool(
        np.max(np.abs(final_rows[:3])) < 1.0e-9
        and np.max(np.abs(final_rows[3:constraint_stop])) < 1.0e-9
        and np.linalg.norm(final_rows[constraint_stop:16]) < 1.0e-7
        and np.linalg.norm(final_rows[-2:]) < 2.0e-5
        and eta["minimum"] > 0.0
    )
    promoted = bool(
        accepted > 0 and final_merit < initial_merit and eta["minimum"] > 0.0
    )
    audit = {
        "classification": "EXACT_NONFLUX_FIBER_WITH_PAIRED_EXACT_FLUX_SLOPES",
        "equivalence": (
            "A(Y)=0_AND_PHI_RESTRICTED_TO_THE_LOCAL_A_FIBER_EQUALS_ZERO_"
            "IFF_THE_UNCHANGED_F18(Y)=0"
        ),
        "nonflux_rows": 16,
        "local_fiber_dimension": 26,
        "new_rows_constraints_or_gates": False,
        "paired_exact_flux_slope_step": pair_step,
        "proposal_trust_radius": trust_radius,
        "paired_exact_residual_evaluations": paired_evaluations,
        "initial_fixed_reference_merit": initial_merit,
        "final_fixed_reference_merit": final_merit,
        "final_raw_residual_norm": final_raw_residual_norm,
        "accepted_steps": accepted,
        "nonflux_projection_requested": project_nonflux_first,
        "nonflux_projection_history": projection_history,
        "message": message,
        "history": history,
        "finite_branch": bool(
            np.all(np.isfinite(state))
            and np.linalg.norm(solver_values) <= 100.0 * max(1.0, bounded_start)
        ),
    }
    if promoted:
        child["child_state"] = {
            "coordinates": state[:qdim].tolist(),
            "velocities": state[qdim:2 * qdim].tolist(),
            "multipliers": state[2 * qdim:].tolist(),
            "binary64_hex": {
                "coordinates": [float(item).hex() for item in state[:qdim]],
                "velocities": [
                    float(item).hex() for item in state[qdim:2 * qdim]
                ],
                "multipliers": [
                    float(item).hex() for item in state[2 * qdim:]
                ],
            },
            "eta_Legendre": eta,
        }
        child["physical_residuals"] = {
            "maximum_trace": float(np.max(np.abs(final_rows[:3]))),
            "maximum_eleven_constraints": float(
                np.max(np.abs(final_rows[3:constraint_stop]))
            ),
            "momentum_norm": float(np.linalg.norm(final_rows[14:16])),
            "dynamic_flux_norm": float(np.linalg.norm(final_rows[-2:])),
        }
        child["complete_child_candidate_validated"] = root_closed
        child["checkpoint_promotion_eligible"] = True
        child["fiber_reduction"] = audit
        child["required_next"] = (
            "EVALUATE_POSITIVE_DURATION_CONSTRAINT_CONSISTENT_RELATIVE_N5_"
            "PERSISTENCE" if root_closed else
            "CONTINUE_THE_UNCHANGED_EXACT_N5_F18_ROOT_ON_THE_VALIDATED_"
            "LOCAL_NONFLUX_FIBER"
        )
        result["N5_event_conditioned_complete_child_reconstruction"] = child
        result["N5_child_fiber_reduction_audit"] = audit
        result["active_dependency"] = child["required_next"]
        payload["cross_resolution_reconnaissance"] = result
        path.write_text(deterministic_json(payload), encoding="utf-8")
    return {
        "promoted": promoted,
        "root_closed": root_closed,
        "initial_merit": initial_merit,
        "final_merit": final_merit,
        "final_raw_residual_norm": final_raw_residual_norm,
        "eta_minimum": eta["minimum"],
        "physical_residuals": child.get("physical_residuals"),
        "audit": audit,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--iterations", type=int, default=8)
    parser.add_argument("--trust-radius", type=float, default=8192.0)
    parser.add_argument("--pair-step", type=float, default=1.0)
    parser.add_argument("--project-nonflux-first", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        continue_n5_fiber(
            args.artifact,
            iterations=args.iterations,
            trust_radius=args.trust_radius,
            pair_step=args.pair_step,
            project_nonflux_first=args.project_nonflux_first,
        ),
        indent=2,
    ))


if __name__ == "__main__":
    main()
