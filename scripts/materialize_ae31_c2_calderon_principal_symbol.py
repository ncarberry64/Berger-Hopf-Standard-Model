"""Materialize the current-C2 Calderon/Hadamard principal symbol."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_calderon_principal_symbol import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    conditional_massive_to_principal_limit,
    gauge_brst_characteristic_symbol,
    local_boundary_symbol_theorem,
    reset_equivariance_witness,
    self_dual_principal_covariance,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_CALDERON_PRINCIPAL_SYMBOL.json"
INPUTS = (
    A / "BHSM_AE31_C2_CALDERON_TRACE_SKELETON.json",
    A / "BHSM_AE31_C2_RESET_HADAMARD_TRANSPORT.json",
    A / "BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",
    ROOT / "src/bhsm/interface/ae31_c2_calderon_principal_symbol.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, complex):
        return {"real": value.real, "imaginary": value.imag}
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    skeleton, transport, gauge = map(_load, INPUTS[:3])
    covariance = self_dual_principal_covariance((0.4, -0.7, 1.1))
    reset = reset_equivariance_witness()
    mass_limit = conditional_massive_to_principal_limit()
    gauge_symbol = gauge_brst_characteristic_symbol()
    theorem = local_boundary_symbol_theorem()
    boundary = claim_boundary()
    covariance_certificate = {
        key: value
        for key, value in covariance.items()
        if key not in {"covariance", "CAR_conjugation_matrix"}
    }
    gauge_certificate = {
        key: value
        for key, value in gauge_symbol.items()
        if key not in {"transverse_projector", "coexact_Hessian_symbol"}
    }
    validation = {
        "trace_skeleton_reused": (
            skeleton["claim_boundary"]["CURRENT_C2_RESET_CALDERON_TRACE_SKELETON_DERIVED"]
        ),
        "Hadamard_transport_reused": (
            transport["claim_boundary"]["AE2_RESET_HADAMARD_STATE_CLASS_TRANSPORT_DERIVED"]
        ),
        "same_gauge_Hessian_reused": (
            gauge["claim_boundary"]["same_C2_continuous_frequency_gauge_ghost_Hessian_derived"]
        ),
        "self_dual_pure_principal_covariance": (
            covariance["Hermitian_residual"] < 1.0e-12
            and covariance["purity_residual"] < 1.0e-12
            and covariance["self_dual_CAR_residual"] < 1.0e-12
        ),
        "reset_and_family_equivariance": (
            reset["principal_covariance_intertwining_residual"] < 1.0e-12
            and reset["CAR_conjugation_intertwining_residual"] < 1.0e-12
            and reset["family_projectors_preserved"]
        ),
        "mass_is_lower_order": (
            mass_limit["strictly_decreasing"]
            and not mass_limit["mass_changes_homogeneous_principal_symbol"]
        ),
        "BRST_characteristic_matching": (
            gauge_symbol["BRST_characteristic_matching_residual"] < 1.0e-12
            and not gauge_symbol["principal_symbol_repairs_residue_mismatch"]
        ),
        "smooth_completion_not_fabricated": (
            not theorem["physical_outer_projector_constructed"]
            and not boundary["CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"]
            and not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
        ),
    }
    return _jsonable(
        {
            "artifact": "BHSM_AE31_C2_CALDERON_PRINCIPAL_SYMBOL",
            "action_version": ACTION_VERSION,
            "classification": CLASSIFICATION,
            "self_dual_principal_covariance_certificate": covariance_certificate,
            "reset_equivariance_witness": reset,
            "conditional_massive_to_principal_limit": mass_limit,
            "gauge_BRST_characteristic_symbol_certificate": gauge_certificate,
            "local_boundary_symbol_theorem": theorem,
            "claim_boundary": boundary,
            "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
            "validation": validation,
            "validation_passed": all(validation.values()),
            "FULL_BHSM_COMPLETE": False,
        }
    )


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 current-C2 Calderon principal symbol failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
