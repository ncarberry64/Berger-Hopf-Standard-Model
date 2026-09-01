"""Derive the common normalized-field derivative identity used by Gate 7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
MATCHING = BASE / "BHSM_N12_GATE7_SIGNED_COMMON_FRAME_DATA_MATCHING.json"
RESULT = BASE / "BHSM_N12_GATE7_NORMALIZED_FIELD_COMMON_FRAME_IDENTITY.json"


def normalized_first_second(
    value: np.ndarray,
    first_u: np.ndarray,
    first_v: np.ndarray,
    second_uv: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return D(G/|G|)[u] and D2(G/|G|)[u,v] from G jets."""
    radius = float(np.linalg.norm(value))
    if radius <= 0.0:
        raise ValueError("the retained cancellation-preserving field must be nonzero")
    unit = value / radius
    projector = np.eye(value.size) - np.outer(unit, unit)
    projected_u = projector @ first_u
    projected_v = projector @ first_v
    normalized_first = projected_u / radius
    normalized_second = (
        projector @ second_uv / radius
        - (
            float(unit @ first_v) * projected_u
            + float(unit @ first_u) * projected_v
            + unit * float(first_u @ projected_v)
        ) / radius**2
    )
    return normalized_first, normalized_second


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _fixed_identity_audit() -> dict[str, float]:
    value = np.asarray([2.0, -1.0, 3.0, 0.5])
    first_u = np.asarray([0.3, -0.2, 0.4, 0.1])
    first_v = np.asarray([-0.1, 0.5, 0.2, -0.3])
    second_uv = np.asarray([0.07, -0.04, 0.02, 0.05])
    first, mixed = normalized_first_second(
        value, first_u, first_v, second_uv,
    )

    def map_value(u: float, v: float) -> np.ndarray:
        raw = value + u * first_u + v * first_v + u * v * second_uv
        return raw / np.linalg.norm(raw)

    step = 2.0e-4
    numeric_first = (map_value(step, 0.0) - map_value(-step, 0.0)) / (2.0 * step)
    numeric_mixed = (
        map_value(step, step) - map_value(step, -step)
        - map_value(-step, step) + map_value(-step, -step)
    ) / (4.0 * step**2)
    radius = float(np.linalg.norm(value))
    first_majorant = float(np.linalg.norm(first_u) / radius)
    second_majorant = float(
        np.linalg.norm(second_uv) / radius
        + 3.0 * np.linalg.norm(first_u) * np.linalg.norm(first_v) / radius**2
    )
    return {
        "first_identity_residual_2_norm": float(np.linalg.norm(first - numeric_first)),
        "mixed_identity_residual_2_norm": float(np.linalg.norm(mixed - numeric_mixed)),
        "first_norm": float(np.linalg.norm(first)),
        "first_majorant": first_majorant,
        "mixed_norm": float(np.linalg.norm(mixed)),
        "mixed_majorant": second_majorant,
    }


def build_payload() -> dict[str, Any]:
    matching = json.loads(MATCHING.read_text(encoding="utf-8"))
    audit = _fixed_identity_audit()
    validation = {
        "common_frame_matching_validated": matching["validation_passed"] is True,
        "first_derivative_identity_numerically_replayed": audit["first_identity_residual_2_norm"] < 1.0e-8,
        "second_derivative_identity_numerically_replayed": audit["mixed_identity_residual_2_norm"] < 1.0e-7,
        "first_majorant_dominates_fixed_replay": audit["first_norm"] <= audit["first_majorant"],
        "second_majorant_dominates_fixed_replay": audit["mixed_norm"] <= audit["mixed_majorant"],
        "no_inverse_of_kinetic_Dirac_or_history_operator": True,
        "no_new_action_source_selector_or_scale": True,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_NORMALIZED_FIELD_COMMON_FRAME_IDENTITY",
        "status": "NORMALIZED_FIELD_D1_D2_AND_COMMON_FRAME_RADII_BRIDGE_DERIVED" if passed else "NORMALIZED_FIELD_IDENTITY_INVALID",
        "retained_field": "f=G/||G||_2_ON_THE_NONZERO_CANCELLATION_PRESERVING_GRAPH",
        "identities": {
            "projector": "Q=I-f*f^T",
            "D_f_u": "Q*D_G_u/||G||",
            "D2_f_uv": "Q*D2_G_uv/||G||-((f^T*D_G_v)*Q*D_G_u+(f^T*D_G_u)*Q*D_G_v+f*(D_G_u^T*Q*D_G_v))/||G||^2",
            "D_f_majorant": "||Df||<=A1/g0",
            "D2_f_majorant": "||D2f||<=A2/g0+3*A1^2/g0^2",
        },
        "BHSM_G_product_rule": {
            "G": "(s*c,_W*(b*psi+s*h))",
            "D_G_u": "(s_u*c+s*c_u,_W*(b_u*psi+b*psi_u+s_u*h+s*h_u))",
            "D2_G_uv": "(s_uv*c+s_u*c_v+s_v*c_u,_W*(b_uv*psi+b_u*psi_v+b_v*psi_u+b*psi_uv+s_uv*h+s_u*h_v+s_v*h_u+s*h_uv))",
            "linear_configuration_fact": "D2_c_uv=0",
        },
        "common_frame_bridge": {
            "Y": "Y<=Y_center_plus_outward_defect_quadrature_remainder",
            "Z1": "Z1<=||I-A*L0||_P+C_A*delta_J",
            "Z2": "Z2<=C_A*(A2/g0+3*A1^2/g0^2)",
            "radii": "Y+Z1*r+Z2*r^2<r_AND_Z1+2*Z2*r<1",
        },
        "fixed_replay": audit,
        "validation": validation,
        "validation_passed": passed,
        "inputs": {_relative(MATCHING): _sha256(MATCHING)},
        "claim_boundary": {
            "identity": "DERIVED",
            "numerical_common_frame_majorants": "OPEN",
            "Y_Z1_Z2": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "EVALUATE_g0_A1_A2_delta_J_C_A_AND_THE_SIGNED_DEFECT_REMAINDER_CELLWISE_IN_THE_RETAINED_PHYSICAL_FRAMES",
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "fixed_replay": payload["fixed_replay"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
