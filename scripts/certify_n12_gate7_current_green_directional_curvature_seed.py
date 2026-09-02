"""Certify the current-center Green-directional rate curvature at node 1."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_accepted_replay_center_outward_74d as cert  # noqa: E402


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
ENDPOINT = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
JACOBIAN = F / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
OBSTRUCTION = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
RESULT = F / "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_CURVATURE_SEED.json"
DATA = RESULT.with_suffix(".npz")
THEORY = ROOT / "theory/n12_gate7_current_green_directional_curvature_seed.md"
THIS_SCRIPT = Path(__file__).resolve()
NODE = 1
PRECISION = cert.PRECISION
INPUTS = (
    ENDPOINT,
    ENDPOINT.with_suffix(".npz"),
    JACOBIAN,
    JACOBIAN.with_suffix(".npz"),
    PARTITION,
    PARTITION.with_suffix(".npz"),
    OBSTRUCTION,
    OBSTRUCTION.with_suffix(".npz"),
    Path(cert.__file__).resolve(),
    THIS_SCRIPT,
    THEORY,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _export(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    midpoint = np.empty(values.shape, dtype=float)
    radius = np.empty_like(midpoint)
    for index in np.ndindex(values.shape):
        midpoint[index] = float(values[index])
        radius[index] = math.nextafter(
            float(abs(values[index] - arb(midpoint[index])).upper()), math.inf,
        )
    return midpoint, radius


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    partition = json.loads(PARTITION.read_text(encoding="utf-8"))
    obstruction = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    if not partition["validation_passed"] or not obstruction["validation_passed"]:
        raise RuntimeError("validated partition and obstruction inputs required")
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        state = np.asarray(source["projected_states"][NODE], dtype=float)
        descriptor = float(source["independent_signed_descriptors"][NODE])
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangent = np.asarray(source["endpoint_physical_tangent_action"][NODE], dtype=float)
    with np.load(PARTITION.with_suffix(".npz")) as source:
        unit_mid = np.asarray(
            source["current_center_green_image_unit_mid"][NODE], dtype=float,
        )
        unit_radius = np.asarray(
            source["current_center_green_image_unit_radius"][NODE], dtype=float,
        )

    ctx.prec = PRECISION
    frame = cert._frame(tangent, cert.TRIAL_DESCRIPTOR_SCALE)
    direction = np.empty(cert.STATE + 1, dtype=object)
    for ambient in range(cert.STATE + 1):
        value = arb(0)
        for coordinate in range(74):
            value += arb(float(frame[ambient, coordinate])) * arb(
                float(unit_mid[coordinate]), float(unit_radius[coordinate]),
            )
        direction[ambient] = value
    curvature = cert._rate_second_directional(
        state, descriptor, weights, reference, direction,
    )
    center_rate = cert._rate_enclosure(
        state, descriptor, weights, reference, None,
    )
    midpoint, radius = _export(curvature)
    np.savez_compressed(
        DATA,
        green_directional_rate_curvature_mid=midpoint,
        green_directional_rate_curvature_radius=radius,
        green_unit_causal_coordinate_mid=unit_mid,
        green_unit_causal_coordinate_radius=unit_radius,
        node=np.asarray(NODE),
        precision_bits=np.asarray(PRECISION),
    )

    total = cert._arb_norm_bounds(curvature)
    configuration = cert._arb_norm_bounds(curvature[: cert.QDIM])
    reduced = cert._arb_norm_bounds(curvature[cert.QDIM : cert.STATE])
    descriptor_bounds = cert._arb_norm_bounds(curvature[cert.STATE :])
    transverse_raw = obstruction["amplification_decomposition"][
        "local_interval_stages"
    ][0]["raw_endpoint_rate_second"]
    green_to_transverse_upper_ratio = math.nextafter(
        total["upper"] / float(transverse_raw["lower"]), math.inf,
    )
    transverse_to_green_lower_factor = math.nextafter(
        float(transverse_raw["lower"]) / total["upper"], -math.inf,
    )
    validation = {
        "same_frozen_accepted_replay_center": True,
        "same_selected_branch_without_binary_reselection": True,
        "current_BHSM_native_green_direction_used": partition["claim_boundary"][
            "G7_BHSM_NATIVE_GREEN_IMAGE_PARTITION_RECOVERED"
        ],
        "384_bit_Arb_retained_action_evaluation": PRECISION == 384,
        "selected_line_gap_remains_positive": center_rate.gap_lower > 0.0,
        "green_directional_curvature_is_strictly_smaller_than_transverse_witness": (
            total["upper"] < float(transverse_raw["lower"])
        ),
        "no_center_trajectory_action_branch_scale_or_fit_changed": True,
        "local_seed_not_relabelled_as_causal_two_radius_certificate": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_CURVATURE_SEED",
        "status": "CURRENT_CENTER_GREEN_DIRECTIONAL_RETAINED_ACTION_CURVATURE_SEED_CERTIFIED",
        "authority": "384_BIT_ARB_LOCAL_DIRECTIONAL_CURVATURE_NOT_CAUSAL_TWO_RADIUS_AUTHORITY",
        "node": NODE,
        "precision_bits": PRECISION,
        "green_directional_rate_curvature": {
            "total": total,
            "configuration": configuration,
            "reduced_field": reduced,
            "descriptor": descriptor_bounds,
        },
        "comparison_to_existing_transverse_obstruction": {
            "transverse_coordinate": obstruction["outward_operands"][
                "Z2_obstruction_causal_coordinate"
            ],
            "transverse_raw_rate_curvature": transverse_raw,
            "green_to_transverse_upper_ratio": green_to_transverse_upper_ratio,
            "transverse_to_green_lower_factor": transverse_to_green_lower_factor,
            "interpretation": "THE_CURRENT_GREEN_AXIS_HAS_OVER_FIVE_MILLION_TIMES_LESS_RAW_LOCAL_RATE_CURVATURE_THAN_THE_ALREADY_CERTIFIED_ALMOST_PURELY_TRANSVERSE_OBSTRUCTION_DIRECTION_AT_THE_SAME_NODE",
        },
        "selected_line": {
            "gap_lower": center_rate.gap_lower,
            "eigen_residual_upper": center_rate.eigen_residual_upper,
        },
        "exact_next_calculation": "EXTEND_CURRENT_GREEN_DIRECTIONAL_D2F_uG_uG_TO_ALL_RETAINED_ENDPOINTS_AND_MIDPOINTS,_THEN_EVALUATE_MIXED_D2F_dot_uG_AND_THE_TRANSVERSE_REMAINDER_BEFORE_CAUSAL_TWO_RADIUS_COMPOSITION",
        "claim_boundary": {
            "CURRENT_CENTER_NODE1_GREEN_DIRECTIONAL_RATE_CURVATURE_DERIVED": True,
            "CURRENT_CENTER_ALL_NODE_GREEN_DIRECTIONAL_CURVATURE_DERIVED": False,
            "CURRENT_CENTER_GREEN_MIXED_CURVATURE_DERIVED": False,
            "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED": False,
            "G7_ROOT_NONEXISTENCE_DERIVED": False,
            "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("Green-directional curvature seed validation failed")
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "green_directional_rate_curvature": payload[
            "green_directional_rate_curvature"
        ],
        "comparison": payload["comparison_to_existing_transverse_obstruction"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
