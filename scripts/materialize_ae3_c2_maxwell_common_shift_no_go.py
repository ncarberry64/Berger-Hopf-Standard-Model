"""Materialize the current-C2 Maxwell common-shift no-go."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_maxwell_common_shift_no_go import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    common_covariant_shift_witness,
    exact_common_shift_no_go,
    muon_chain_boundary,
    required_noncommon_correction,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE3_C2_MAXWELL_COMMON_SHIFT_NO_GO.json"
INPUTS = (
    A / "BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",
    A / "BHSM_AE31_C2_COMPOSITE_LORENTZIAN_KINETIC_POLE.json",
    ROOT / "src/bhsm/interface/ae3_c2_maxwell_common_shift_no_go.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    gauge, matter = map(_load, INPUTS[:2])
    shift = common_covariant_shift_witness(2.5)
    theorem = exact_common_shift_no_go()
    required = required_noncommon_correction()
    chain = muon_chain_boundary()
    boundary = claim_boundary()
    validation = {
        "parent_mismatch_reused": (
            gauge["claim_boundary"]["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"] is False
            and theorem["parent_difference_Zs_minus_Zt"] > 0.0
        ),
        "matter_local_Lorentzian_residue_context_reused": (
            matter["claim_boundary"]["CURRENT_C2_COMPOSITE_TEMPORAL_SPATIAL_POLE_RESIDUE_MATCH_DERIVED"]
        ),
        "common_shift_difference_invariant": (
            shift["relative_difference_invariance_residual"] < 1.0e-15
            and shift["shifted_form_positive"]
            and not shift["one_Maxwell_residue_after_finite_common_shift"]
        ),
        "scope_not_overstated": (
            not theorem["all_quantum_or_boundary_corrections_excluded"]
            and not boundary["CURRENT_C2_ALL_QUANTUM_GAUGE_REPAIRS_EXCLUDED"]
        ),
        "required_noncommon_difference_not_fitted": (
            required["required_delta_Zt_minus_delta_Zs"] > 0.0
            and not required["one_candidate_selected_by_current_action"]
            and not required["coefficient_fitted_to_required_difference"]
        ),
        "photon_and_muon_not_overclaimed": (
            not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
            and not boundary["CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
            and not chain["muon_vertex_F2_zero_ready"]
        ),
    }
    return {
        "artifact": "BHSM_AE3_C2_MAXWELL_COMMON_SHIFT_NO_GO",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "common_covariant_shift_witness": shift,
        "exact_common_shift_no_go": theorem,
        "required_noncommon_correction": required,
        "muon_chain_boundary": chain,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3 current-C2 Maxwell common-shift no-go failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
