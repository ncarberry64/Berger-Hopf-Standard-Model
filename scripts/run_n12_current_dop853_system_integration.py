"""Run existing boundary-response APIs on the current stored DOP853 center.

This samples the stored degree-seven polynomial, without solving a new orbit.
Stored exact macro-node action rates recover the proper-time density
N*s/||G|| without another action evaluation. ``--clock retained-field``
evaluates that density on the native fine mesh instead.
Existing gauge/BRST and product-Dirac routines then evaluate that coefficient
path. Optional supplied six-sector event blocks activate the existing KKT and
Noether composition. No certificate status is an execution prerequisite.

Example:
    python scripts/run_n12_current_dop853_system_integration.py --workers 2

``--operator-bundle`` accepts an NPZ with ``<sector>_parent``,
``<sector>_coupling``, and ``<sector>_child`` for each existing SECTOR_ORDER,
plus response_operator, source, response_target, and an anti-Hermitian
generator. These must be values on this same center and common domain.
No missing block is replaced by a synthetic or zero block.
``--mode-response-report`` attaches an existing finite-history mode response
only when its center SHA256 matches this DOP853 input. Its discretization,
scope, and diagnostics remain those of that original numerical run.
``--coupled-children`` computes the connected coefficient/mixed-form/parent
load calculation using that mode report and its companion arrays. This uses
the actual48-node macro mesh and its existing z=-1 boundary probe separately
from this runner's configurable fine-mesh boundary probe. Its gradient is
owned by the first stored C2 frontier; incoming formation coordinates need
their action-owned seed-to-frontier pullback.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import eigvalsh
from scipy.special import exp1, logsumexp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.run_n12_current_environment_child_coupling import evaluate_couplings
from scripts.run_n12_current_coupled_environment_children import (
    evaluate_current_coupled_environment_children,
)

from bhsm.interface.aether_cancelled_arc_proper_time_pullback import pullback_cancelled_arc_history_to_proper_time
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from bhsm.interface.aether_forward_c2_finite_core_descriptor import assemble_finite_core_descriptor
from bhsm.interface.forward_finite_endpoint_heat_force import (
    finite_core_heat_trace_log_upper_bound,
    piecewise_linear_zeta_coefficient_cotangent,
)
from bhsm.interface.aether_forward_c2_fast_cancelled_field import (
    exact_cancelled_euler_dirac_field_action,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (
    boundary_geometry_action_covectors,
)
from bhsm.interface.ae4_current_c2_affine72_particle_fiber_calderon import (
    attach_preserved_particle_fibers,
)
from bhsm.interface.ae4_current_c2_stop_gauge_brst_calderon import (
    stop_gauge_brst_calderon,
)
from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    SECTOR_ORDER,
    assemble_stratified_direct_sum,
    canonical_noether_flux_balance,
    solve_retarded_event_kkt,
)

DEFAULT_CENTER = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)
DEFAULT_FIBERS = ROOT / (
    "artifacts/action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
)
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/dop853_system_integration"


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _canonical(value.tolist())
    if isinstance(value, np.generic):
        return _canonical(value.item())
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def _dense(left: np.ndarray, coefficients: np.ndarray, fraction: float) -> np.ndarray:
    """Evaluate the stored SciPy DOP853 polynomial in its native order."""
    value = np.zeros_like(left)
    for index, coefficient in enumerate(reversed(coefficients)):
        value += coefficient
        value *= fraction if index % 2 == 0 else 1.0 - fraction
    return value + left


def _load_center(path: Path, stride: int, subdivisions: int, clock: str) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as source:
        grid = np.asarray(source["fine_grid_action_lengths"], dtype=float)
        values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        stop_index = int(source["stop_bracket_fine_grid_index"][0])
        stop_fraction = float(source["stop_dense_fraction"][0])
        macro_arc = np.asarray(source["action_lengths"], dtype=float)
        macro_states = np.asarray(source["centers"], dtype=float)
        macro_descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        macro_rates = np.asarray(source["action_rates"], dtype=float)
    if stride < 1 or subdivisions < 1:
        raise ValueError("positive stride and subdivisions required")
    if (weights.shape != (98,) or reference.shape != (61,)
            or values.shape != (grid.size, 99)
            or coefficients.shape != (grid.size - 1, 7, 99)
            or np.any(weights <= 0) or np.any(np.diff(grid) <= 0)
            or not 0 < stop_fraction <= 1 or not 0 <= stop_index < coefficients.shape[0]):
        raise ValueError("aligned current N12 DOP853 center arrays required")
    arc: list[float] = []
    augmented: list[np.ndarray] = []
    for interval in range(0, stop_index + 1, stride):
        right_fraction = stop_fraction if interval == stop_index else 1.0
        width = grid[interval + 1] - grid[interval]
        for fraction in np.arange(subdivisions, dtype=float) * right_fraction / subdivisions:
            arc.append(float(grid[interval] + width * fraction))
            augmented.append(_dense(values[interval], coefficients[interval], float(fraction)))
    stop_arc = float(grid[stop_index] + stop_fraction * (grid[stop_index + 1] - grid[stop_index]))
    terminal = _dense(values[stop_index], coefficients[stop_index], stop_fraction)
    terminal_raw_descriptor = float(terminal[-1])
    terminal[-1] = 0.0  # The stored action-selected first-stop face is s=0.
    arc.append(stop_arc)
    augmented.append(terminal)
    sampled = np.asarray(augmented)
    if clock == "stored-macro":
        arc = macro_arc.tolist()
        sampled = np.column_stack((macro_states * weights, macro_descriptors))
        # The producer evaluates these same polynomials at macro nodes and
        # explicitly stores the native polynomial terminal with s=0.
        if not np.isclose(macro_arc[-1], stop_arc, rtol=0, atol=1e-12):
            raise ValueError("stored macro stop does not match native DOP853 stop")
        if not np.allclose(sampled[-1, :-1], terminal[:-1], rtol=0, atol=1e-12):
            raise ValueError("stored macro terminal differs from native DOP853 terminal")
        sampled[-1] = terminal
    if not np.all(np.isfinite(sampled)) or np.any(sampled[:-1, -1] < 0):
        raise ArithmeticError("sampled stored center left its finite positive-descriptor domain")
    return {
        "arc": np.asarray(arc), "states": sampled[:, :-1] / weights,
        "descriptor": sampled[:, -1], "weights": weights, "reference": reference,
        "source_intervals": stop_index + 1, "terminal_dense_descriptor": terminal_raw_descriptor,
        "macro_action_rates": macro_rates,
    }


def _density_sample(task: tuple[int, np.ndarray, float, np.ndarray, np.ndarray]) -> dict[str, Any]:
    index, state, descriptor, weights, reference = task
    # Keep the combined-direction retained evaluator; a process-wide JAX
    # predictor flag must not silently change this numerical execution.
    os.environ["BHSM_N12_FAST_DELTA_JAX"] = "0"
    field = exact_cancelled_euler_dirac_field_action(
        state=state, weights=weights, reference=reference, signed_descriptor=descriptor,
    )
    geometry = boundary_geometry_action_covectors(state=state, weights=weights)
    norm = float(np.linalg.norm(field["cancelled_field_action"]))
    if not np.isfinite(norm) or norm <= 0:
        raise ArithmeticError("cancelled-field norm must be finite and positive")
    return {
        "node": index, "cancelled_field_action_norm": norm,
        "log_radius": float(geometry["log_R4"]),
        "log_lapse": float(geometry["log_lapse"]),
        "selected_branch": int(field["selected_branch"]),
        "selected_line_gap": float(field["selected_eigenline_gap"]),
    }


def _density_rows(center: dict[str, Any], workers: int, cache: Path, key: str, clock: str) -> list[dict[str, Any]]:
    center["density_rows_loaded_from_cache"] = False
    if clock == "stored-macro":
        q_weights = metric_data()[0]
        rows = []
        for index, (state, descriptor, rate) in enumerate(zip(
                center["states"], center["descriptor"], center["macro_action_rates"], strict=True)):
            configuration = q_weights * state[37:74]
            square = float(configuration @ configuration)
            if not np.isfinite(square) or square <= 0:
                raise ArithmeticError("nonzero stored configuration velocity required for clock recovery")
            alpha = float(rate[:37] @ configuration) / square
            # G_q=s*q_weights*v, so dY_q/dr=alpha*q_weights*v
            # with alpha=s/||G||. Recover the product without dividing by s.
            if index == len(center["arc"]) - 1 and descriptor == 0:
                alpha = 0.0
            if alpha < 0 or not np.isfinite(alpha):
                raise ArithmeticError("stored proper-time clock factor must be finite and nonnegative")
            geometry = boundary_geometry_action_covectors(state=state, weights=center["weights"])
            rows.append({"node": index, "log_radius": float(geometry["log_R4"]),
                         "log_lapse": float(geometry["log_lapse"]),
                         "proper_time_density": float(np.exp(geometry["log_lapse"]) * alpha),
                         "configuration_rate_alignment_relative_residual": float(
                             np.linalg.norm(rate[:37] - alpha * configuration) / max(np.linalg.norm(rate[:37]), np.finfo(float).tiny))})
        print(json.dumps({"stage": "proper_time_density", "stored_exact_macro_rates": len(rows)}), flush=True)
        return rows
    if cache.is_file():
        saved = json.loads(cache.read_text(encoding="utf-8"))
        if saved.get("key") == key:
            center["density_rows_loaded_from_cache"] = True
            print(json.dumps({"stage": "proper_time_density", "cached_nodes": len(saved["rows"])}), flush=True)
            return saved["rows"]
    tasks = [(i, state, float(s), center["weights"], center["reference"])
             for i, (state, s) in enumerate(zip(center["states"], center["descriptor"], strict=True))]
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(_density_sample, tasks, chunksize=1):
            rows.append(row)
            if len(rows) % 16 == 0 or len(rows) == len(tasks):
                print(json.dumps({"stage": "proper_time_density", "completed": len(rows), "total": len(tasks)}), flush=True)
    cache.write_text(json.dumps({"key": key, "rows": rows}, indent=2) + "\n", encoding="utf-8")
    return rows


def _event_response(path: Path) -> dict[str, Any]:
    """Compose explicitly supplied values through the existing event APIs."""
    with np.load(path, allow_pickle=False) as source:
        required = [f"{sector}_{name}" for sector in SECTOR_ORDER for name in ("parent", "coupling", "child")]
        required += ["response_operator", "source", "response_target", "generator"]
        missing = [key for key in required if key not in source]
        if missing:
            raise ValueError("operator bundle missing: " + ", ".join(missing))
        sectors = {sector: tuple(np.asarray(source[f"{sector}_{name}"])
                                  for name in ("parent", "coupling", "child")) for sector in SECTOR_ORDER}
        blocks = assemble_stratified_direct_sum(sectors)
        response = solve_retarded_event_kkt(
            parent_block=blocks["parent_block"], parent_child_coupling=blocks["parent_child_coupling"],
            child_retarded_block=blocks["child_retarded_block"],
            response_operator=source["response_operator"], source=source["source"], response_target=source["response_target"],
        )
        noether = canonical_noether_flux_balance(trace=response["parent_trace"], event_tractions=response["event_tractions"], generator=source["generator"])
    return {"operator_bundle": str(path.resolve()), "direct_sum": blocks, "response": response, "noether": noether}


def _heat_zeta(log_radius: np.ndarray, durations: np.ndarray) -> dict[str, Any]:
    """Evaluate inherited finite-core channels at the retained heat length."""
    channels = (("coexact", "scalar", 4.0, 1), ("BRST_scalar", "scalar", 3.0, 1),
                ("product_Dirac_plus", "product_Dirac", 1.5, 1),
                ("product_Dirac_minus", "product_Dirac", 1.5, -1))
    rows = {}
    for name, kind, coefficient, chirality in channels:
        pencil = assemble_finite_core_descriptor(log_radii=log_radius, proper_durations=durations,
                                                channel=kind, unit_channel_value=coefficient, chirality=chirality)
        def dense(diagonal: np.ndarray, off: np.ndarray) -> np.ndarray:
            return np.diag(diagonal) + np.diag(off, 1) + np.diag(off, -1)
        bound_args = {"dimension": pencil["dimension"], "proper_duration_upper": float(durations.sum()), "heat_length": 1.0}
        if kind == "scalar":
            bound_args["scalar_potential_lower"] = float(np.min(pencil["element_coefficient"]))
        else:
            bound_args["factorization_coefficient_upper"] = float(np.max(np.abs(pencil["element_coefficient"])))
        row = {"dimension": pencil["dimension"], "channel": kind, "chirality": chirality,
               "heat_length": 1.0, "finite_core_heat_bound": finite_core_heat_trace_log_upper_bound(**bound_args)}
        try:
            eigenvalues = eigvalsh(dense(pencil["K_diagonal"], pencil["K_off_diagonal"]),
                                  dense(pencil["M_diagonal"], pencil["M_off_diagonal"]))
            row["minimum_generalized_eigenvalue"] = float(eigenvalues[0])
            if np.all(np.isfinite(eigenvalues)) and eigenvalues[0] > 0:
                row.update({"numerical_heat_evaluation": "EVALUATED", "Gamma_heat": float(-0.5 * exp1(eigenvalues).sum()),
                            "heat_trace": float(np.exp(-eigenvalues).sum()),
                            "log_heat_trace": float(-eigenvalues[0] + logsumexp(-(eigenvalues - eigenvalues[0]))),
                            "binary64_heat_underflow": bool(np.exp(-eigenvalues).sum() == 0)})
            else:
                row["numerical_heat_evaluation"] = "FLOAT64_GENERALIZED_PENCIL_DID_NOT_RETURN_A_POSITIVE_FINITE_SPECTRUM"
        except (ValueError, np.linalg.LinAlgError) as exc:
            row["numerical_heat_evaluation"] = "FLOAT64_GENERALIZED_PENCIL_FAILED"
            row["numerical_failure"] = str(exc)
        rows[name] = row
    return {"finite_core_channels": rows,
            "BRST_inherited_multiplicities": {"constraint": 2, "complex_ghost_graded": -2},
            "BRST_same_operator_heat_cancellation": 0.0,
            "coexact_inherited_multiplicity": 3,
            "product_Dirac_family_multiplicity_not_invented": True,
            "zeta": piecewise_linear_zeta_coefficient_cotangent(log_radius, durations),
            "scope": "FINITE_CORE_CHANNELS_AND_RETAINED_ZETA_TERM;_NOT_COMPLETE_INTERACTING_SIX_SECTOR_SUPERTRACE"}


def _load_mode_response(path: Path | None, source_hash: str) -> dict[str, Any] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("physical mode response report must be a JSON object")
    reported_hash = payload.get("center_SHA256")
    if not isinstance(reported_hash, str) or reported_hash.lower() != source_hash.lower():
        raise ValueError(
            "physical mode response center SHA256 does not match the DOP853 input: "
            f"report={reported_hash!r}, input={source_hash}"
        )
    return payload


def run(args: argparse.Namespace) -> dict[str, Any]:
    source_hash = hashlib.sha256(args.center.read_bytes()).hexdigest()
    physical_modes = _load_mode_response(args.mode_response_report, source_hash)
    if args.coupled_children and args.mode_response_report is None:
        raise ValueError("--coupled-children requires --mode-response-report and its companion arrays.npz")
    if args.coupled_children:
        mode_dir = args.mode_response_report.resolve().parent
        if not (mode_dir / "arrays.npz").is_file():
            raise ValueError("coupled children require actual mode arrays.npz beside the mode response report")
        standard_report = _load_mode_response(mode_dir / "report.json", source_hash)
        if standard_report != physical_modes:
            raise ValueError("supplied mode response report differs from the companion mode directory's report.json")
    center = _load_center(args.center, args.interval_stride, args.subdivisions, args.clock)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    cache_key = source_hash + f":{args.interval_stride}:{args.subdivisions}:{args.clock}:retained_combined_direction"
    rows = _density_rows(center, args.workers, output / "density_cache.json", cache_key, args.clock)
    count = len(rows)
    empty = np.empty((count, 0), dtype=float)
    density = np.asarray([r["proper_time_density"] for r in rows]) if args.clock == "stored-macro" else (
        np.exp(np.asarray([r["log_lapse"] for r in rows])) * center["descriptor"]
        / np.asarray([r["cancelled_field_action_norm"] for r in rows]))
    pulled = pullback_cancelled_arc_history_to_proper_time(
        arc_nodes=center["arc"], log_radius=np.asarray([r["log_radius"] for r in rows]),
        log_radius_arc_first_jet=empty, proper_time_density=density,
        proper_time_density_first_jet=empty,
    )
    proper_durations = np.diff(pulled["proper_times"])
    print(json.dumps({"stage": "boundary_operators", "segments": count - 1, "proper_duration": pulled["proper_duration"]}), flush=True)
    gauge = stop_gauge_brst_calderon(
        log_radii=pulled["log_radius"], proper_durations=proper_durations,
        spectral_parameter=args.spectral_parameter, friedrichs_terminal_selected=True,
        decimal_precision=args.decimal_precision,
    )
    fibers = json.loads(args.fibers.read_text(encoding="utf-8"))["family_mode_C2_instantiation"]["rows"]
    attached = attach_preserved_particle_fibers(
        log_radii=pulled["log_radius"], normalized_proper_times=pulled["normalized_proper_times"],
        proper_duration=pulled["proper_duration"], log_radius_first_jet=empty,
        proper_duration_first_jet=np.empty(0), frozen_fiber_rows=fibers,
        spatial_dirac_level=0, spectral_parameter=args.spectral_parameter,
    )
    heat_zeta = _heat_zeta(pulled["log_radius"], proper_durations)
    missing = []
    event = None
    if args.operator_bundle:
        event = _event_response(args.operator_bundle)
    else:
        missing = [f"{sector}: H_pp, H_pc, H_cc_retarded" for sector in SECTOR_ORDER]
        missing += ["common-domain response_operator, source, response_target, symmetry generator"]
    np.savez_compressed(output / "coefficient_path.npz", arc_nodes=center["arc"], states=center["states"],
                        signed_descriptor=center["descriptor"], log_radius=pulled["log_radius"],
                        proper_times=pulled["proper_times"], proper_durations=proper_durations,
                        proper_time_density=pulled["proper_time_density"])
    environment = evaluate_couplings(coefficient_path=output / "coefficient_path.npz", fibers=args.fibers,
                                     decimal_precision=args.decimal_precision,
                                     spectral_parameter=args.spectral_parameter)
    coupled = None
    coupled_probe = None
    if args.coupled_children:
        coupled = evaluate_current_coupled_environment_children(
            mode_dir=args.mode_response_report.resolve().parent,
            output=output / "coupled_children", center=args.center,
        ).report
        coupled_probe = {
            "main_boundary_spectral_parameter": args.spectral_parameter,
            "coupled_macro_boundary_spectral_parameter": -1.0,
            "boundary_probes_match": args.spectral_parameter == -1.0,
            "known_minus_zeta_action_component_depends_on_boundary_probe": False,
            "scope": "CONNECTED_CURRENT48_MACRO_NODE_CHILD_JETS;_MAIN_COEFFICIENT_MESH_REMAINS_SEPARATE",
            "column_coordinates": {
                "coordinate_owner": coupled["known_parent_action_component"]["coordinate_owner"],
                "callback_coordinate_maps": "operator_jets['parent_coordinates']",
                "full73_mixed_jet_basis": "parent_coordinates.full73_state_action_basis:98_BY_73_CURRENT_WEIGHTED_ACTION_COLUMNS",
                "fixed_birth72_map_in_full73": "parent_coordinates.fixed_birth72_to_full73:73_BY_72",
                "projected72_mixed_arrays": "plus/minus *_first_jet*_birth72",
                "default_parent_gradient": "98_COMPONENT_ACTION_DUAL_PROJECTED_ONTO_INITIAL_MODE_ACTION_TIMES_Q72",
                "basis_arrays": coupled["outputs"]["mixed_operator_jets"],
                "incoming_E1_formation_Gamma_y_connected": False,
                "incoming_formation_role": "LAUNCH_COMPONENT_AFTER_OWNED_SEED_TO_FRONTIER_PULLBACK",
            },
        }
    return _canonical({
        "status": "CURRENT_DOP853_BOUNDARY_RESPONSES_EVALUATED",
        "center": str(args.center.resolve()), "center_sha256": source_hash,
        "numerical_path": {"source_intervals": center["source_intervals"], "sampled_nodes": count,
                           "clock": args.clock, "interval_stride": args.interval_stride if args.clock == "retained-field" else None,
                           "subdivisions": args.subdivisions if args.clock == "retained-field" else None,
                           "stop_action_length": float(center["arc"][-1]),
                           "terminal_descriptor_before_stop_face": center["terminal_dense_descriptor"],
                           "proper_duration": pulled["proper_duration"],
                           "selected_branches_seen": sorted({r["selected_branch"] for r in rows if "selected_branch" in r}),
                           "minimum_sampled_selected_line_gap": min((r["selected_line_gap"] for r in rows if "selected_line_gap" in r), default=None),
                           "maximum_clock_alignment_relative_residual": max((r["configuration_rate_alignment_relative_residual"] for r in rows if "configuration_rate_alignment_relative_residual" in r), default=None),
                           "sampling_and_proper_time_quadrature": "STORED_DOP853_SAMPLES_AND_TRAPEZOIDAL_N_S_OVER_CANCELLED_FIELD_NORM"},
        "gauge_BRST_response": gauge, "particle_fiber_response": attached,
        "heat_zeta_response": heat_zeta,
        "environment_child_coupling": environment,
        "physical_mode_response": physical_modes,
        "physical_mode_response_report": str(args.mode_response_report.resolve()) if args.mode_response_report else None,
        "coupled_environment_children": coupled,
        "coupled_environment_children_boundary_probe": coupled_probe,
        "particle_fiber_parameter_jet_count": 0,
        "event_response": event, "event_response_missing_inputs": missing,
        "HS_mixed_sector_missing_inputs": ["action-owned HS source profile and common-domain fermion-HS coupling"],
        "execution": {"trajectory_reintegrated": False, "certificate_status_used_as_execution_gate": False,
                      "operator_blocks_invented": False, "synthetic_KKT_witness_used": False,
                      "density_sample_cache_reused": center["density_rows_loaded_from_cache"],
                      "new_exact_action_evaluations": count if args.clock == "retained-field" and not center["density_rows_loaded_from_cache"] else 0,
                      "decimal_precision": args.decimal_precision},
        "physical_observables": {"masses_poles_vertices_collisions_computed": False},
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--fibers", type=Path, default=DEFAULT_FIBERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--clock", choices=("stored-macro", "retained-field"), default="stored-macro",
                        help="recover density from stored exact 48-node action rates, or evaluate on the native fine mesh")
    parser.add_argument("--interval-stride", type=int, default=1, help="1 covers every stored interval; larger values provide a coarse smoke run")
    parser.add_argument("--subdivisions", type=int, default=1, help="coefficient samples per visited DOP853 interval")
    parser.add_argument("--spectral-parameter", type=float, default=-1.0, help="existing negative-axis resolvent probe")
    parser.add_argument("--decimal-precision", type=int, default=60)
    parser.add_argument("--operator-bundle", type=Path)
    parser.add_argument("--mode-response-report", type=Path,
                        help="attach a completed finite-history mode response on this same center SHA256")
    parser.add_argument("--coupled-children", action="store_true",
                        help="compute same-center macro child jets, mixed operators and known partial parent load using the supplied mode report")
    args = parser.parse_args()
    if args.workers < 1 or args.decimal_precision < 50 or args.spectral_parameter >= 0:
        parser.error("workers>=1, decimal precision>=50, and spectral parameter<0 required")
    payload = run(args)
    target = args.output.resolve() / "report.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report": str(target),
                      "proper_duration": payload["numerical_path"]["proper_duration"],
                      "attached_particle_fibers": payload["particle_fiber_response"]["attached_fiber_count"],
                      "BRST_cancellation_residual": payload["gauge_BRST_response"]["BRST_cancellation_residual_norm"],
                      "environment_couplings_evaluated": payload["environment_child_coupling"]["status"],
                      "new_exact_action_evaluations": payload["execution"]["new_exact_action_evaluations"],
                      "physical_mode_response_attached": payload["physical_mode_response"] is not None,
                      "coupled_children_evaluated": payload["coupled_environment_children"] is not None,
                      "event_response_executed": payload["event_response"] is not None}, indent=2), flush=True)


if __name__ == "__main__":
    main()
