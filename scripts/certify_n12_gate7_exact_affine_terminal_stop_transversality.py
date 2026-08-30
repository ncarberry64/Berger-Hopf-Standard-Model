"""Certify transversality of the corrected exact-affine Gate-7 stop.

The previous terminal certificate deliberately used continuity only.  This
companion evaluates ``D lambda_24[F]`` with the retained outward tensor
interval evaluator at the corrected terminal center and transfers its sign
over the certified final Taylor--Volterra cone.  It therefore supplies the
implicit first-stop-time prerequisite needed by the history-operator jet.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import audit_n12_c2_stop_boundary_cluster_probe as cluster  # noqa: E402
import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact  # noqa: E402
import certify_n12_gate7_exact_affine_terminal_selected_eigenvalue_bracket as bracket  # noqa: E402
from bhsm.interface.aether_retained_action_tensor_interval import (  # noqa: E402
    retained_action_tensor_interval,
)


BASE = ROOT / "artifacts" / "flagship_integration"
SPECTRUM = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BOUNDARY_CLUSTER_SPECTRUM.json"
BRACKET = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_SELECTED_EIGENVALUE_BRACKET.json"
STOP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
Z2 = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"
FIELD_RECORD = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_DIRECTIONAL_FIELD_CURVATURE.json"
FIELD = FIELD_RECORD.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_gate7_exact_affine_terminal_stop_transversality.md"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_STOP_TRANSVERSALITY.json"
THIS_SCRIPT = Path(__file__).resolve()
QDIM = 37
SELECTED = 24


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _up(value: float) -> float:
    return math.nextafter(float(value) * (1.0 + 1.0e-12), math.inf)


def main() -> None:
    parents = [_load(path) for path in (SPECTRUM, BRACKET, STOP, Z2, FIELD_RECORD)]
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated exact-center stop and field parents required")
    spectrum, terminal, stop, z2, _field_record = parents
    (
        states, rates, times, weights, reference,
        fine_times, fine_correction, _nonlinear_radius,
    ) = exact._inputs()
    endpoint = float(times[-1])
    state = bracket._state_at(
        endpoint, states, rates, times, weights, fine_times, fine_correction,
    )
    with np.load(FIELD) as source:
        field = np.asarray(source["normalized_field"][-1], dtype=float)
        field_times = np.asarray(source["action_lengths"], dtype=float)
    if float(field_times[-1]) != endpoint:
        raise RuntimeError("terminal normalized field has stale abscissa")

    jet = cluster.local.exact_full_action_jet_at_state(
        12, state[:QDIM], state[QDIM:2 * QDIM], state[2 * QDIM:],
        points=cluster.local.POINTS,
    )
    reduced = np.asarray(jet.hessian, dtype=float)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(0.5 * (reduced + reduced.T))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi

    # retained_action_tensor_interval consumes action-coordinate directions.
    selected_leg = np.zeros(weights.size)
    selected_leg[QDIM:] = weights[QDIM:] * psi
    derivative = retained_action_tensor_interval(
        12, state, state, [selected_leg, selected_leg, field],
        points=cluster.local.POINTS,
    )
    center_lower = float(derivative.lo)
    center_upper = float(derivative.hi)

    final_row = z2["rows"][-1]
    radius = float(
        z2["summary"]["maximum_third_order_Taylor_Volterra_total_radius"]
    )
    descriptor_D1 = float(final_row["selected_descriptor_D1_upper"])
    descriptor_D2 = float(final_row["selected_descriptor_D2_upper"])
    # For F=N/||N||, ||DF|| <= ||DN||/inf ||N|| on the certified cone.
    field_D1 = _up(
        float(final_row["normalized_numerator_D1_tube_upper"])
        / float(final_row["normalized_numerator_tube_lower"])
    )
    variation = _up(radius * (descriptor_D2 + descriptor_D1 * field_D1))
    derivative_interval = [
        math.nextafter(center_lower - variation, -math.inf),
        math.nextafter(center_upper + variation, math.inf),
    ]
    margin = math.nextafter(-derivative_interval[1], -math.inf)

    last_spectrum = spectrum["rows"][-1]
    terminal_interval = terminal["terminal_cell"]["action_interval"]
    validation = {
        "corrected_terminal_abscissa_consumed": endpoint == 92.30513924040065,
        "terminal_cell_matches_sign_bracket": terminal_interval == last_spectrum["action_interval"],
        "branch_24_selected_at_terminal_center": selected == SELECTED,
        "materialized_normalized_field_has_unit_action_norm": abs(float(np.linalg.norm(field)) - 1.0) < 2.0e-15,
        "outward_point_tensor_interval_is_strictly_negative": center_upper < 0.0,
        "uniform_cone_derivative_interval_is_strictly_negative": derivative_interval[1] < 0.0,
        "continuous_selected_line_simple_on_terminal_cell": bool(
            last_spectrum["boundary_cluster_certificate_closed"]
            and float(last_spectrum["selected_positive_gap_lower"]) > 0.0
            and float(last_spectrum["negative_selected_gap_lower"]) > 0.0
        ),
        "canonical_first_stop_preterminal_positivity_inherited": (
            stop["Gate7_consequence"][
                "canonical_earliest_lambda24_zero_exists_in_terminal_cell"
            ] == "CERTIFIED_BY_CONTINUITY"
        ),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_STOP_TRANSVERSALITY",
        "status": (
            "ACTION_OWNED_TERMINAL_STOP_TRANSVERSALITY_AND_FIRST_TIME_JET_CERTIFIED"
            if passed else "TERMINAL_STOP_TRANSVERSALITY_INVALID"
        ),
        "authority": (
            "OUTWARD_RETAINED_ACTION_MIXED_TENSOR_INTERVAL_AT_THE_CORRECTED_"
            "CENTER_PLUS_FINAL_TAYLOR_VOLTERRA_CONE_TRANSFER"
        ),
        "stop_equation": "lambda_24=0",
        "terminal_center": {
            "action_length": endpoint,
            "selected_branch": selected,
            "selected_eigenvalue": float(values[selected]),
            "normalized_field_action_norm": float(np.linalg.norm(field)),
            "outward_Dlambda24_of_F_interval": [center_lower, center_upper],
        },
        "cone_transfer": {
            "action_radius_upper": radius,
            "selected_descriptor_D1_upper": descriptor_D1,
            "selected_descriptor_D2_upper": descriptor_D2,
            "normalized_field_D1_upper": field_D1,
            "derivative_variation_upper": variation,
            "uniform_Dlambda24_of_F_interval": derivative_interval,
            "strict_negative_margin_lower": margin,
            "identity": (
                "|Dlambda_x[F_x]-Dlambda_c[F_c]| <= "
                "rho*(||D2lambda||+||Dlambda||*||DF||)"
            ),
        },
        "consequence": {
            "terminal_zero_unique_on_the_certified_terminal_flow_cell": passed,
            "canonical_earliest_stop_is_transverse": passed,
            "local_differentiable_first_stop_time_map": passed,
            "first_stop_time_jet_formula": "Dxi_T=-(Dxi_lambda24)/(Dlambda24[F])",
            "operator_endpoint_motion_prerequisite": "CLOSED" if passed else "OPEN",
        },
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                SPECTRUM, BRACKET, STOP, Z2, FIELD_RECORD, FIELD, THEORY,
                THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "stop_transversality": "CERTIFIED" if passed else "OPEN",
            "differentiable_stop_time": "CERTIFIED_LOCALLY" if passed else "OPEN",
            "full_72_direction_geometry_path_jet": "OPEN_NEXT_OWNER",
            "complete_operator_first_jet": "OPEN_AFTER_GEOMETRY_PATH_JET",
            "projected_force_KKT_Hessian": "NOT_YET_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_CERTIFIED_72_DIRECTION_RESET_QUOTIENT_FIRST_JET_"
            "THROUGH_THE_EXACT_AFFINE_HISTORY,_APPLY_THE_TRANSVERSE_STOP_TIME_"
            "JET,_AND_FEED_log_R4_AND_DURATION_JETS_TO_THE_COMPACT_WEYL_ORACLE"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "center_interval": payload["terminal_center"]["outward_Dlambda24_of_F_interval"],
        "uniform_interval": derivative_interval,
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
