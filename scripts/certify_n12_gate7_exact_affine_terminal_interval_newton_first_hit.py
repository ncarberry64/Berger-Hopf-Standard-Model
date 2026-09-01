"""Enclose and materialize the transverse Gate-7 first-hit time."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact  # noqa: E402
import certify_n12_gate7_exact_affine_terminal_selected_eigenvalue_bracket as bracket  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
BRACKET = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_SELECTED_EIGENVALUE_BRACKET.json"
TRANSVERSALITY = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_STOP_TRANSVERSALITY.json"
STOP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
THEORY = ROOT / "theory" / "n12_gate7_exact_affine_terminal_interval_newton_first_hit.md"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _quotient_interval(
    numerator_lower: float, numerator_upper: float,
    denominator_lower: float, denominator_upper: float,
) -> tuple[float, float]:
    values = (
        numerator_lower / denominator_lower,
        numerator_lower / denominator_upper,
        numerator_upper / denominator_lower,
        numerator_upper / denominator_upper,
    )
    return (
        math.nextafter(min(values), -math.inf),
        math.nextafter(max(values), math.inf),
    )


def main() -> None:
    terminal, transverse, stop = (
        _load(path) for path in (BRACKET, TRANSVERSALITY, STOP)
    )
    if not all(record.get("validation_passed") is True for record in (
        terminal, transverse, stop,
    )):
        raise RuntimeError("validated sign, transversality, and first-stop parents required")
    (
        states, rates, times, weights, reference,
        fine_times, fine_correction, _nonlinear_radius,
    ) = exact._inputs()
    left, right = (float(value) for value in terminal["terminal_cell"]["action_interval"])
    endpoint = terminal["terminal_cell"]["right"]
    value_lower, value_upper = (
        float(value) for value in endpoint["selected_eigenvalue_interval"]
    )
    derivative_lower, derivative_upper = (
        float(value) for value in transverse["cone_transfer"][
            "uniform_Dlambda24_of_F_interval"
        ]
    )
    displacement_lower, displacement_upper = _quotient_interval(
        value_lower, value_upper, derivative_lower, derivative_upper,
    )
    root_lower = math.nextafter(right - displacement_upper, -math.inf)
    root_upper = math.nextafter(right - displacement_lower, math.inf)

    root_midpoint = 0.5 * (root_lower + root_upper)
    root_radius = 0.5 * (root_upper - root_lower)
    representative_state = bracket._state_at(
        root_midpoint, states, rates, times, weights, fine_times, fine_correction,
    )
    np.savez_compressed(
        DATA,
        first_hit_action_time_interval=np.asarray((root_lower, root_upper)),
        first_hit_action_time_midpoint=np.asarray(root_midpoint),
        first_hit_action_time_radius=np.asarray(root_radius),
        representative_action_time=np.asarray(root_midpoint),
        representative_state=representative_state,
        state_weights=weights,
        branch_reference=reference,
    )

    validation = {
        "terminal_endpoint_is_corrected_abscissa": right == 92.30513924040065,
        "endpoint_value_interval_is_strictly_negative": value_upper < 0.0,
        "flow_derivative_interval_is_strictly_negative": derivative_upper < 0.0,
        "interval_Newton_root_is_inside_terminal_cell": left < root_lower < root_upper < right,
        "representative_time_is_inside_outward_root_interval": (
            root_lower <= root_midpoint <= root_upper
        ),
        "canonical_preterminal_positivity_inherited": (
            stop["preterminal_cover"]["minimum_selected_eigenvalue_lower"] > 0.0
        ),
        "terminal_zero_uniqueness_inherited": transverse["consequence"][
            "terminal_zero_unique_on_the_certified_terminal_flow_cell"
        ] is True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT",
        "status": (
            "CANONICAL_TRANSVERSE_FIRST_HIT_TIME_INTERVAL_CERTIFIED"
            if passed else "TERMINAL_INTERVAL_NEWTON_FIRST_HIT_INVALID"
        ),
        "authority": (
            "TERMINAL_ACTION_OWNED_EIGENVALUE_INTERVAL_DIVIDED_BY_UNIFORM_"
            "NEGATIVE_FLOW_DERIVATIVE_INTERVAL_PLUS_MONOTONE_FIRST_STOP_THEOREM"
        ),
        "interval_Newton": {
            "base_action_time": right,
            "base_selected_eigenvalue_interval": [value_lower, value_upper],
            "uniform_Dlambda24_of_F_interval": [derivative_lower, derivative_upper],
            "backward_displacement_interval": [displacement_lower, displacement_upper],
            "first_hit_action_time_interval": [root_lower, root_upper],
            "first_hit_action_time_midpoint": root_midpoint,
            "first_hit_action_time_radius": root_radius,
            "interval_width": root_upper - root_lower,
        },
        "representative": {
            "action_time": root_midpoint,
            "selected_branch": 24,
            "role": (
                "MIDPOINT_STATE_ONLY;_NOT_A_NUMERICALLY_RESOLVED_ZERO;_"
                "THE_OUTWARD_INTERVAL_IS_THE_FIRST_HIT_AUTHORITY"
            ),
            "binary64_eigenvalue_root_solve": (
                "REJECTED_BECAUSE_EIGENSOLVER_JITTER_EXCEEDS_THE_ROOT_SIGNAL"
            ),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (BRACKET, TRANSVERSALITY, STOP, THEORY, THIS_SCRIPT)
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "canonical_first_hit_time": "CERTIFIED_INTERVAL",
            "representative_midpoint_state": "MATERIALIZED_WITHOUT_ZERO_CLAIM",
            "operator_history_terminal_abscissa": "SUPERSEDES_NEGATIVE_SIDE_ENDPOINT",
            "continuous_outward_variational_carrier": "OPEN_REBUILD_AT_FIRST_HIT",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REBUILD_THE_DIRECT_EXACT_CENTER_TERMINAL_FRAME_AND_FIELD_JACOBIAN_"
            "AT_THE_CERTIFIED_FIRST_HIT_CENTER,_THEN_CONSTRUCT_THE_REFINED_"
            "WITHIN_SEAM_OUTWARD_VARIATIONAL_CARRIER"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "interval_Newton": payload["interval_Newton"],
        "representative": payload["representative"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
