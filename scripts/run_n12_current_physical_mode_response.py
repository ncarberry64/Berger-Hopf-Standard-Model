"""Evaluate constrained numerical mode response on the retained N12 history.

The unchanged action supplies the graph Jacobian and 25 constraint rows.
Second-order Magnus transport uses its stored macro centers. Singular gains
refer to the retained weighted action norm over this finite history. They do
not diagnose equilibrium stability, select a child, or replace the current
continuous-path certificate. No historical incoming Q66 frame is consumed.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "JAX_NUM_THREADS", "TF_NUM_INTRAOP_THREADS", "TF_NUM_INTEROP_THREADS"):
    os.environ[_name] = "1"
os.environ.setdefault("XLA_FLAGS", "--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1")

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.linalg import null_space
from scipy.sparse.linalg import expm_multiply

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from bhsm.interface.aether_forward_c2_fast_cancelled_field import exact_cancelled_euler_dirac_field_action
from bhsm.interface.aether_hybrid_c2_graph_jacobian import graph_jacobian_action
from recon_n12_c2_stop_physical_tangent_transfer import _constraint_geometry

DEFAULT_CENTER = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
DEFAULT_OUT = ROOT / "artifacts/current_runtime/current_physical_mode_response"


def _norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, 2))


def _condition(singular: np.ndarray) -> float | None:
    if singular[-1] <= 0 or not np.isfinite(singular[0] / singular[-1]):
        return None
    return float(singular[0] / singular[-1])


def _gains(singular: np.ndarray) -> dict[str, object]:
    """Report gains and numerical scale without inferring mode stability."""
    roundoff_scale = float(np.finfo(float).eps * len(singular) * singular[0])
    return dict(maximum=float(singular[0]), minimum=float(singular[-1]),
                condition_number=_condition(singular),
                estimated_svd_roundoff_scale=roundoff_scale,
                smallest_gain_roundoff_sensitive=bool(singular[-1] <= roundoff_scale),
                singular_gains=singular.tolist(),
                classification_scope="BINARY64_FINITE_HISTORY_GAIN_NOT_ASYMPTOTIC_STABILITY")


def _actual_cancelled(state, descriptor, rate, weights, reference):
    """Recover the actual stored normalization; evaluate it at the stop face."""
    qweights = metric_data()[0]
    numerator_q = descriptor * qweights * state[37:74]
    denominator = float(rate[:37] @ rate[:37])
    if descriptor != 0 and denominator > 0:
        norm = float(numerator_q @ rate[:37] / denominator)
        if not np.isfinite(norm) or norm <= 0:
            raise ValueError("positive stored action-field normalization required")
        replay = float(np.linalg.norm(norm * rate[:37] - numerator_q) / np.linalg.norm(numerator_q))
        return norm * rate, norm, replay, "STORED_EXACT_ACTION_RATE_AND_CONFIGURATION_IDENTITY"
    value = exact_cancelled_euler_dirac_field_action(
        state=state, weights=weights, reference=reference,
        signed_descriptor=float(descriptor))
    cancelled = np.asarray(value["cancelled_field_action"], dtype=float)
    norm = float(np.linalg.norm(cancelled))
    replay = float(np.linalg.norm(cancelled / norm - rate))
    return cancelled, norm, replay, "RETAINED_ACTION_FIELD_EVALUATED_AT_STOP"


def run(center: Path, out: Path, node_indices: list[int] | None) -> dict[str, object]:
    started = time.perf_counter()
    with np.load(center, allow_pickle=False) as z:
        states, descriptors, arc, rates, weights, reference = (
            np.asarray(z[name], dtype=float) for name in
            ("centers", "signed_descriptors", "action_lengths", "action_rates",
             "state_weights", "branch_reference"))
    if (states.ndim != 2 or states.shape[1] != 98 or weights.shape != (98,)
            or reference.shape != (61,) or rates.shape != states.shape
            or descriptors.shape != (len(states),) or arc.shape != descriptors.shape
            or np.any(np.diff(arc) <= 0) or np.any(weights <= 0)):
        raise ValueError("aligned retained N12 state/rate/metric arrays required")
    indices = list(range(len(states))) if node_indices is None else node_indices
    if len(indices) < 2 or indices != sorted(set(indices)) or indices[0] < 0 or indices[-1] >= len(states):
        raise ValueError("at least two increasing current macro-node indices required")
    out.mkdir(parents=True, exist_ok=True)
    rows, jacobians, tangents, constraints, gradients = [], [], [], [], []
    for count, index in enumerate(indices, 1):
        point_started = time.perf_counter()
        cancelled, norm, replay, norm_owner = _actual_cancelled(
            states[index], float(descriptors[index]), rates[index], weights, reference)
        result = graph_jacobian_action(states[index], weights, reference,
            float(descriptors[index]), cancelled_field_action=cancelled)
        if result["selected_branch"] != 24:
            raise RuntimeError("current selected branch changed")
        geometry = _constraint_geometry((index, states[index], weights))
        C, Q = geometry[1:3]
        if Q.shape != (98, 73):
            raise RuntimeError("current 25-constraint tangent does not have dimension73")
        J = np.asarray(result["graph_Jacobian_action"], dtype=float)
        reduced = Q.T @ J @ Q
        symmetric = np.linalg.eigvalsh((reduced + reduced.T) / 2)
        rows.append(dict(node=index, action_arc=float(arc[index]), selected_branch=24,
            selected_line_gap=float(result["selected_eigenline_gap"]),
            tangent_dimension=73, normalized_constraint_min_singular=float(geometry[5][-1]),
            constraint_value_norm=float(np.linalg.norm(geometry[3])),
            normalized_constraint_flow_residual=float(np.linalg.norm(C @ rates[index])),
            reduced_jacobian_operator_norm=_norm(reduced),
            instantaneous_symmetric_action_arc_rate_min=float(symmetric[0]),
            instantaneous_symmetric_action_arc_rate_max=float(symmetric[-1]),
            cancelled_field_norm=norm, normalization_owner=norm_owner,
            normalization_replay=replay, point_seconds=time.perf_counter()-point_started))
        jacobians.append(J); tangents.append(Q); constraints.append(C)
        gradients.append(np.asarray(result["descriptor_gradient_action"], dtype=float))
        print(json.dumps(dict(completed=count, total=len(indices), **rows[-1])), flush=True)

    jacobians, tangents, constraints, gradients = map(np.asarray,
        (jacobians, tangents, constraints, gradients))
    times = arc[indices]
    ambient = tangents[0].copy()
    quotient = np.eye(73)
    step_maps, leakage, ambient_loss, flow_replay = [], [], [], []
    for k, width in enumerate(np.diff(times)):
        generator = 0.5 * (jacobians[k] + jacobians[k+1])
        both = expm_multiply(float(width) * generator,
                             np.column_stack((tangents[k], ambient, rates[indices[k]])))
        evolved, ambient = both[:, :73], both[:, 73:146]
        target = tangents[k+1]
        step_map = target.T @ evolved
        quotient = step_map @ quotient
        step_maps.append(step_map)
        leakage.append(_norm(evolved - target @ step_map))
        ambient_loss.append(_norm(constraints[k+1] @ ambient))
        flow_replay.append(float(np.linalg.norm(both[:, -1] - rates[indices[k+1]])))
    projected_ambient = tangents[-1].T @ ambient
    left, singular, right = np.linalg.svd(projected_ambient, full_matrices=False)
    projected_singular = np.linalg.svd(quotient, compute_uv=False)
    normal = ambient - tangents[-1] @ projected_ambient
    summary = dict(node_count=len(indices), tangent_dimension=73,
        first_action_arc=float(times[0]), last_action_arc=float(times[-1]),
        full_current_macro_history=indices == list(range(len(states))),
        unconstrained_transport_projected_at_endpoint=_gains(singular),
        tangent_projection_at_each_macro_step=_gains(projected_singular),
        endpoint_normal_leakage_operator=_norm(normal),
        endpoint_normal_leakage_relative=_norm(normal)/max(_norm(ambient), np.finfo(float).tiny),
        endpoint_normalized_constraint_loss_operator=float(ambient_loss[-1]),
        maximum_step_tangent_leakage_operator=float(max(leakage)),
        maximum_propagated_normalized_constraint_loss=float(max(ambient_loss)),
        maximum_step_flow_transport_residual=float(max(flow_replay)),
        maximum_constraint_value_norm=max(r["constraint_value_norm"] for r in rows),
        maximum_constraint_flow_residual=max(r["normalized_constraint_flow_residual"] for r in rows),
        elapsed_seconds=time.perf_counter()-started)
    np.savez_compressed(out / "arrays.npz", node_indices=np.asarray(indices),
        action_lengths=times, graph_Jacobian_action=jacobians,
        descriptor_gradient_action=gradients, physical_tangent_action=tangents,
        normalized_constraint_action=constraints, physical_step_maps=np.asarray(step_maps),
        physical_fundamental=quotient, unprojected_ambient_fundamental=ambient,
        endpoint_projected_ambient_fundamental=projected_ambient,
        singular_gains=singular, initial_mode_coefficients=right.T,
        terminal_mode_coefficients=left,
        initial_mode_action=tangents[0] @ right.T,
        initial_mode_raw=(tangents[0] @ right.T)/weights[:, None],
        terminal_mode_action=tangents[-1] @ left,
        step_tangent_leakage=np.asarray(leakage),
        propagated_constraint_loss=np.asarray(ambient_loss),
        step_flow_transport_residual=np.asarray(flow_replay))
    report = dict(status="CURRENT_N12_CONSTRAINED_FINITE_HISTORY_MODE_RESPONSE_EVALUATED",
        center=str(center.resolve()), center_SHA256=hashlib.sha256(center.read_bytes()).hexdigest().upper(),
        domain="CURRENT_BRANCH24__25_EULER_DIRAC_AND_ZERO_ENERGY_CONSTRAINTS__73_TANGENT",
        norm="UNCHANGED_WEIGHTED_ACTION_NORM_USING_CURRENT_STATE_WEIGHTS",
        transport="SECOND_ORDER_TRAPEZOIDAL_MAGNUS_ON_SELECTED_STORED_MACRO_CENTERS",
        scientific_scope="NUMERICAL_CENTER_FINITE_HISTORY_RESPONSE; MACRO_DISCRETIZATION_AND_TANGENT_LEAKAGE_REPORTED",
        equilibrium_stability="NOT_DETERMINED_BY_FINITE_HISTORY_SINGULAR_GAINS",
        external_environment_response="NOT_INFERRED_FROM_LOCAL_GRAPH_JACOBIAN",
        trajectory_reintegrated=False, incoming_branch23_Q66_used=False,
        summary=summary, rows=rows, arrays=str((out / "arrays.npz").resolve()),
        continuous_path_certified=False, FULL_BHSM_COMPLETE=False)
    (out / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=False), flush=True)
    return report


def _cached_transport(jacobians, tangents, constraints, rates, times, subdivisions):
    """Time-order linearly interpolated cached J, without action reevaluation."""
    ambient = tangents[0].copy()
    quotient = np.eye(73)
    step_maps, leakage, loss, flow_replay = [], [], [], []
    for k, width in enumerate(np.diff(times)):
        both = np.column_stack((tangents[k], ambient, rates[k]))
        for substep in range(subdivisions):
            fraction = (substep + 0.5) / subdivisions
            generator = ((1.0 - fraction) * jacobians[k]
                         + fraction * jacobians[k+1])
            both = expm_multiply(float(width / subdivisions) * generator, both)
            if not np.all(np.isfinite(both)):
                raise FloatingPointError(
                    f"nonfinite cached transport at macro {k}, substep {substep}")
        evolved, ambient = both[:, :73], both[:, 73:146]
        target = tangents[k+1]
        step = target.T @ evolved
        quotient = step @ quotient
        step_maps.append(step)
        leakage.append(_norm(evolved - target @ step))
        loss.append(_norm(constraints[k+1] @ ambient))
        flow_replay.append(float(np.linalg.norm(both[:, -1] - rates[k+1])))
    endpoint = tangents[-1].T @ ambient
    left, gains, right = np.linalg.svd(endpoint, full_matrices=False)
    normal = ambient - tangents[-1] @ endpoint
    return dict(ambient=ambient, endpoint=endpoint, quotient=quotient,
                step_maps=np.asarray(step_maps), leakage=np.asarray(leakage),
                loss=np.asarray(loss), flow_replay=np.asarray(flow_replay),
                left=left, gains=gains, right=right,
                normal_leakage=_norm(normal),
                relative_normal_leakage=_norm(normal)/max(_norm(ambient), np.finfo(float).tiny))


def refine_cached(out: Path) -> dict[str, object]:
    """Compare 1/2/4 cached transport steps, retaining residuals beside gains."""
    started = time.perf_counter()
    report_path = out / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    center = Path(report["center"])
    if hashlib.sha256(center.read_bytes()).hexdigest().upper() != report["center_SHA256"]:
        raise ValueError("cached response center no longer matches actual input")
    with np.load(out / "arrays.npz", allow_pickle=False) as z:
        arrays = {key: np.array(z[key]) for key in z.files}
    with np.load(center, allow_pickle=False) as z:
        rates = np.asarray(z["action_rates"], dtype=float)[arrays["node_indices"]]
        weights = np.asarray(z["state_weights"], dtype=float)
    jacobians, tangents, constraints, times = (arrays[key] for key in
        ("graph_Jacobian_action", "physical_tangent_action", "normalized_constraint_action", "action_lengths"))
    results, records = [], []
    for subdivisions in (1, 2, 4):
        try:
            result = _cached_transport(jacobians, tangents, constraints, rates, times, subdivisions)
        except (FloatingPointError, np.linalg.LinAlgError, ValueError) as exc:
            report["cached_transport_failure"] = dict(subdivisions=subdivisions,
                exception=type(exc).__name__, message=str(exc))
            report["equilibrium_stability"] = "UNRESOLVED_NUMERICAL_TRANSPORT_FAILURE"
            report_path.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
            raise
        record = dict(subdivisions_per_macro=subdivisions, gains=_gains(result["gains"]),
            endpoint_normal_leakage_operator=result["normal_leakage"],
            endpoint_normal_leakage_relative=result["relative_normal_leakage"],
            endpoint_normalized_constraint_loss_operator=float(result["loss"][-1]),
            maximum_propagated_normalized_constraint_loss=float(np.max(result["loss"])),
            maximum_step_flow_transport_residual=float(np.max(result["flow_replay"])),
            maximum_step_tangent_leakage_operator=float(np.max(result["leakage"])))
        if results:
            prior = results[-1]
            record["relative_endpoint_matrix_change_from_previous"] = _norm(
                result["endpoint"] - prior["endpoint"])/max(_norm(result["endpoint"]), np.finfo(float).tiny)
            record["maximum_sorted_gain_relative_change_from_previous"] = float(np.max(
                np.abs(result["gains"] - prior["gains"])/np.maximum(result["gains"], np.finfo(float).tiny)))
        records.append(record); results.append(result)
        print(json.dumps({key:value for key,value in record.items() if key != "gains"}
            | dict(maximum_gain=float(result["gains"][0]), minimum_gain=float(result["gains"][-1])),
            allow_nan=False), flush=True)
    finest = results[-1]
    summary = report["summary"]
    summary.update(unconstrained_transport_projected_at_endpoint=_gains(finest["gains"]),
        tangent_projection_at_each_macro_step=_gains(np.linalg.svd(finest["quotient"], compute_uv=False)),
        endpoint_normal_leakage_operator=finest["normal_leakage"],
        endpoint_normal_leakage_relative=finest["relative_normal_leakage"],
        endpoint_normalized_constraint_loss_operator=float(finest["loss"][-1]),
        maximum_step_tangent_leakage_operator=float(np.max(finest["leakage"])),
        maximum_propagated_normalized_constraint_loss=float(np.max(finest["loss"])),
        maximum_step_flow_transport_residual=float(np.max(finest["flow_replay"])),
        output_transport_subdivisions_per_macro=4,
        cached_transport_refinements=records,
        cached_transport_refinement_seconds=time.perf_counter()-started)
    arrays.update(physical_step_maps=finest["step_maps"], physical_fundamental=finest["quotient"],
        unprojected_ambient_fundamental=finest["ambient"],
        endpoint_projected_ambient_fundamental=finest["endpoint"],
        singular_gains=finest["gains"], initial_mode_coefficients=finest["right"].T,
        terminal_mode_coefficients=finest["left"],
        initial_mode_action=tangents[0] @ finest["right"].T,
        initial_mode_raw=(tangents[0] @ finest["right"].T)/weights[:, None],
        terminal_mode_action=tangents[-1] @ finest["left"],
        step_tangent_leakage=finest["leakage"], propagated_constraint_loss=finest["loss"],
        step_flow_transport_residual=finest["flow_replay"],
        transport_refinement_subdivisions=np.asarray((1, 2, 4)),
        transport_refinement_singular_gains=np.asarray([r["gains"] for r in results]),
        transport_refinement_endpoint_matrices=np.asarray([r["endpoint"] for r in results]),
        transport_refinement_constraint_loss=np.asarray([r["loss"] for r in results]),
        transport_refinement_flow_replay=np.asarray([r["flow_replay"] for r in results]))
    initial_flow = tangents[0].T @ rates[0]
    terminal_flow = tangents[-1].T @ rates[-1]
    initial_flow /= np.linalg.norm(initial_flow)
    terminal_flow /= np.linalg.norm(terminal_flow)
    arrays["mode_initial_flow_cosine"] = np.abs(finest["right"] @ initial_flow)
    arrays["mode_terminal_flow_cosine"] = np.abs(finest["left"].T @ terminal_flow)
    reconstructed = (finest["left"] * finest["gains"]) @ finest["right"]
    mode_equation = finest["endpoint"] @ finest["right"].T - finest["left"] * finest["gains"]
    replay = dict(all_numeric_arrays_finite=all(np.all(np.isfinite(x)) for x in arrays.values()),
        maximum_tangent_action_orthogonality_operator=max(
            _norm(q.T @ q - np.eye(73)) for q in tangents),
        maximum_constraint_tangent_annihilator_operator=max(
            _norm(c @ q) for c, q in zip(constraints, tangents)),
        endpoint_svd_matrix_reconstruction_relative=_norm(finest["endpoint"] - reconstructed)/_norm(finest["endpoint"]),
        mode_equation_relative=_norm(mode_equation)/_norm(finest["endpoint"]),
        initial_mode_action_orthogonality_operator=_norm(
            arrays["initial_mode_action"].T @ arrays["initial_mode_action"] - np.eye(73)),
        raw_to_action_mode_conversion_replay=_norm(
            arrays["initial_mode_raw"] * weights[:, None] - arrays["initial_mode_action"]),
        largest_gain_mode_initial_flow_cosine=float(arrays["mode_initial_flow_cosine"][0]),
        largest_gain_mode_terminal_flow_cosine=float(arrays["mode_terminal_flow_cosine"][0]),
        interpretation="FINITE_NUMERICAL_MATRIX_REPLAYS_ONLY__NO_EQUILIBRIUM_OR_INTERVAL_STABILITY_CERTIFICATE")
    (out / "numerical_replay.json").write_text(json.dumps(replay, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    report["numerical_replay"] = replay
    np.savez_compressed(out / "arrays.npz", **arrays)
    report["transport"] = "TIME_ORDERED_EXPONENTIAL_MIDPOINT_1_2_4_SUBSTEPS_OF_LINEARLY_INTERPOLATED_CACHED_J"
    report["cached_transport_refinement_scope"] = (
        "ASSESS_TIME_ORDERING_SENSITIVITY_ONLY; UNSAMPLED_ACTION_JACOBIAN_CURVATURE_ERROR_IS_NOT_BOUNDED")
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--node-indices", type=int, nargs="+")
    parser.add_argument("--refine-cached", action="store_true",
                        help="Refine existing output Jacobians without action evaluations")
    args = parser.parse_args()
    if not args.refine_cached:
        run(args.center, args.out, args.node_indices)
    refine_cached(args.out)


if __name__ == "__main__":
    main()
