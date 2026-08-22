"""Certify paired-step convergence of the N12 center momentum Hessian."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np


COARSE = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_COARSE",
    ".tmp_direct_n12_center_momentum_hessian.npz",
))
HALF = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_HALF",
    ".tmp_direct_n12_center_momentum_hessian_half.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_RICHARDSON",
    ".tmp_direct_n12_center_momentum_hessian_richardson.npz",
))
METADATA = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_CONVERGENCE",
    ".tmp_direct_n12_center_momentum_hessian_convergence.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    coarse = np.load(COARSE)
    half = np.load(HALF)
    if not np.array_equal(coarse["center_state"], half["center_state"]):
        raise ValueError("paired momentum Hessians use different centers")
    if not np.array_equal(coarse["normal_basis"], half["normal_basis"]):
        raise ValueError("paired momentum Hessians use different normal bases")
    records = {}
    richardson = {}
    for name in ("event", "child", "mismatch"):
        coarse_value = np.asarray(coarse[name], dtype=float)
        half_value = np.asarray(half[name], dtype=float)
        extrapolated = (4.0 * half_value - coarse_value) / 3.0
        richardson[name] = extrapolated
        records[name] = {
            "coarse_Frobenius_norm": float(np.linalg.norm(coarse_value)),
            "half_Frobenius_norm": float(np.linalg.norm(half_value)),
            "half_minus_coarse_Frobenius_norm": float(np.linalg.norm(
                half_value - coarse_value
            )),
            "Richardson_Frobenius_norm": float(np.linalg.norm(extrapolated)),
            "Richardson_minus_half_Frobenius_norm": float(np.linalg.norm(
                extrapolated - half_value
            )),
            "Richardson_relative_step_defect": float(
                np.linalg.norm(extrapolated - half_value)
                / max(np.linalg.norm(extrapolated), 1.0e-300)
            ),
            "Richardson_component_operator_norms": [
                float(np.linalg.norm(extrapolated[index], 2))
                for index in range(extrapolated.shape[0])
            ],
        }
    np.savez_compressed(
        RESULT,
        **richardson,
        center_state=half["center_state"],
        normal_basis=half["normal_basis"],
    )
    passed = all(
        record["Richardson_relative_step_defect"] < 1.0e-5
        for record in records.values()
    )
    payload = {
        "classification": (
            "N12_CENTER_MOMENTUM_HESSIAN_PAIRED_STEP_CONVERGED"
            if passed else
            "N12_CENTER_MOMENTUM_HESSIAN_STEP_CONVERGENCE_FAILED"
        ),
        "coarse": str(COARSE),
        "coarse_SHA256": _sha256(COARSE),
        "half": str(HALF),
        "half_SHA256": _sha256(HALF),
        "Richardson": str(RESULT),
        "Richardson_SHA256": _sha256(RESULT),
        "records": records,
        "validation": {
            "same_center_state": True,
            "same_normal_basis": True,
            "paired_step_relative_defect_below_1e-5": passed,
            "center_measurement_is_full_ball_majorant": False,
            "unchanged_F12": True,
        },
        "validation_passed": passed,
        "exact_next_dependency": (
            "BOUND_THE_CANONICAL_MOMENTUM_HESSIAN_VARIATION_ON_THE_"
            "2E-11_ACTION_BALL_FROM_THE_RETAINED_ACTION_MIXED_FIFTH_"
            "VARIATION_AND_CERTIFIED_BORDERED_INVERSES"
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    METADATA.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
