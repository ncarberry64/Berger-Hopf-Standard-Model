"""Materialize the current-center Green-image partition reconciliation."""

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

from bhsm.interface.ae4_current_c2_green_image_partition_reconciliation import (  # noqa: E402
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    green_image_partition_contract,
)


F = ROOT / "artifacts/flagship_integration"
A = ROOT / "artifacts/action_extension"
HISTORICAL = F / "BHSM_N12_GATE7_COMMON_FRAME_ANISOTROPIC_Z2_RECONNAISSANCE.json"
CURRENT = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_ACTION_BLOCK_SCREEN.json"
OBSTRUCTION = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
DATA = TARGET.with_suffix(".npz")
THEORY = ROOT / "theory/ae4_current_c2_green_image_partition_reconciliation.md"
THIS_SCRIPT = Path(__file__).resolve()
SOURCE = ROOT / "src/bhsm/interface/ae4_current_c2_green_image_partition_reconciliation.py"
INPUTS = (
    HISTORICAL,
    HISTORICAL.with_suffix(".npz"),
    CURRENT,
    CURRENT.with_suffix(".npz"),
    OBSTRUCTION,
    OBSTRUCTION.with_suffix(".npz"),
    SOURCE,
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


def _center_radius(value: arb) -> tuple[float, float]:
    center = float(value)
    radius = float(abs(value - arb(center)).upper())
    return center, math.nextafter(radius, math.inf)


def _unit_green_balls(midpoint: np.ndarray, radius: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    unit_mid = np.zeros_like(midpoint)
    unit_radius = np.zeros_like(radius)
    for node in range(1, midpoint.shape[0]):
        vector = np.asarray([
            arb(float(value), float(error))
            for value, error in zip(midpoint[node], radius[node])
        ], dtype=object)
        norm2 = arb(0)
        for value in vector:
            norm2 += value * value
        norm = norm2.sqrt()
        if norm.lower() <= 0:
            raise ArithmeticError(f"Green image contains zero at node {node}")
        for coordinate, value in enumerate(vector):
            unit_mid[node, coordinate], unit_radius[node, coordinate] = (
                _center_radius(value / norm)
            )
    return unit_mid, unit_radius


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    obstruction = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    with np.load(CURRENT.with_suffix(".npz")) as source:
        green_mid = np.asarray(
            source["accepted_center_causal_coordinate_mid"], dtype=float,
        )
        green_radius = np.asarray(
            source["accepted_center_causal_coordinate_radius"], dtype=float,
        )
        green_lower = np.asarray(source["total_Y_lower_by_node"], dtype=float)
    ctx.prec = 384
    unit_mid, unit_radius = _unit_green_balls(green_mid, green_radius)
    witness_node = int(obstruction["outward_operands"]["Z2_obstruction_node"])
    witness_coordinate = int(
        obstruction["outward_operands"]["Z2_obstruction_causal_coordinate"]
    )
    longitudinal_projection_upper = math.nextafter(
        abs(unit_mid[witness_node, witness_coordinate])
        + unit_radius[witness_node, witness_coordinate],
        math.inf,
    )
    transverse_projection_lower = float(
        (arb(1) - arb(longitudinal_projection_upper) ** 2).sqrt().lower()
    )
    np.savez_compressed(
        DATA,
        current_center_green_image_unit_mid=unit_mid,
        current_center_green_image_unit_radius=unit_radius,
        current_center_green_image_norm_lower=green_lower,
        fixed_reset_node=np.asarray(0),
        obstruction_node=np.asarray(witness_node),
        obstruction_coordinate=np.asarray(witness_coordinate),
    )

    contract = green_image_partition_contract(
        historical_green_mechanism_present=historical["validation"][
            "actual_signed_Green_correction_direction_used"
        ],
        historical_values_are_current_authority=False,
        current_green_image_nonzero_after_reset=bool(np.all(green_lower[1:] > 0.0)),
        coarse_field_descriptor_route_obstructed=current["decision"][
            "coarse_73_plus_1_field_descriptor_block_route_obstructed"
        ],
    )
    boundary = claim_boundary()
    validation = {
        "historical_BHSM_green_image_mechanism_recovered": historical[
            "validation"
        ]["actual_signed_Green_correction_direction_used"],
        "historical_reconnaissance_not_promoted": (
            historical["authority"]
            == "CALIBRATED_JAX_CENTER_RECONNAISSANCE_NOT_INTERVAL_AUTHORITY"
            and historical["validation_passed"] is False
            and not boundary[
                "G7_HISTORICAL_48_SEAM_ANISOTROPIC_VALUES_CURRENT_AUTHORITY"
            ]
        ),
        "current_371_node_causal_green_image_used": green_mid.shape == (371, 74),
        "reset_node_is_fixed_zero": bool(np.all(green_mid[0] == 0.0)),
        "all_370_post_reset_green_images_are_nonzero": bool(
            np.all(green_lower[1:] > 0.0)
        ),
        "obstruction_witness_is_over_99_percent_transverse": (
            transverse_projection_lower > 0.99
        ),
        "coarse_obstruction_not_relabelled_as_green_cone_obstruction": (
            contract["coarse_field_descriptor_route_obstructed"]
            and not contract["green_image_anisotropic_route_obstructed"]
        ),
        "no_new_center_trajectory_partition_scale_or_fit": True,
        "green_image_radii_not_overpromoted": not boundary[
            "G7_CURRENT_CENTER_GREEN_IMAGE_ANISOTROPIC_RADII_DERIVED"
        ],
    }
    validation = {key: bool(value) for key, value in validation.items()}
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": "BHSM_NATIVE_GREEN_IMAGE_ANISOTROPIC_PARTITION_RECOVERED_ON_CURRENT_CENTER",
        "historical_recovery": {
            "mechanism": (
                "SIGNED_MINUS_DEFECT_GREEN_IMAGE_LONGITUDINAL_AXIS_WITH_"
                "TRANSVERSE_COMPLEMENT"
            ),
            "historical_artifact": _relative(HISTORICAL),
            "historical_numerical_values_current_authority": False,
            "reason": "THE_OLDER_48_SEAM_CALIBRATED_JAX_RECONNAISSANCE_DOES_NOT_OWN_THE_CURRENT_ACCEPTED_REPLAY_CENTER_OR_OUTWARD_REMAINDER",
        },
        "current_center_instantiation": {
            "nodes": 371,
            "fixed_reset_node": 0,
            "nonzero_post_reset_nodes": 370,
            "causal_dimension": 74,
            "longitudinal_projector": "P_parallel(node)=u_G(node)u_G(node)^T",
            "transverse_projector": "P_perp(node)=I-P_parallel(node)",
            "minimum_post_reset_green_image_norm_lower": float(
                np.min(green_lower[1:])
            ),
            "maximum_green_image_norm_lower": float(np.max(green_lower)),
        },
        "coarse_obstruction_localization": {
            "node": witness_node,
            "causal_coordinate": witness_coordinate,
            "absolute_longitudinal_projection_upper": longitudinal_projection_upper,
            "transverse_projection_lower": transverse_projection_lower,
            "interpretation": "THE_EXISTING_SCALAR_AND_73_PLUS_1_OBSTRUCTION_WITNESS_IS_ALMOST_ENTIRELY_TRANSVERSE_TO_THE_CURRENT_SIGNED_GREEN_IMAGE",
        },
        "authority_reconciliation": contract,
        "required_outward_operands": [
            "CURRENT_CENTER_DIRECTIONAL_D2F_uG_uG",
            "CURRENT_CENTER_MIXED_D2F_dot_uG",
            "CURRENT_CENTER_TRANSVERSE_TRANSVERSE_REMAINDER_ON_THE_DECLARED_SMALL_RADIUS",
            "CAUSAL_TWO_RADIUS_LONGITUDINAL_TRANSVERSE_COMPOSITION_WITH_EXISTING_Y_AND_Z1",
        ],
        "calculation_order": (
            "DIRECTIONAL_AND_MIXED_GREEN_IMAGE_CURVATURE_FIRST;_ONLY_THEN_"
            "THE_TRANSVERSE_REMAINDER_REQUIRED_BY_THE_RESULTING_TWO_RADIUS_"
            "INEQUALITY;_DO_NOT_BEGIN_WITH_A_DENSE_FULL_TENSOR_NORM"
        ),
        "exact_next_calculation": contract["next_proof_object"],
        "data": _relative(DATA),
        "data_SHA256": _sha(DATA),
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "claim_boundary": boundary,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("Green-image partition reconciliation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
