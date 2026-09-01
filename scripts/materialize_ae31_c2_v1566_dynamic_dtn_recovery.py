"""Materialize the continuous-frequency v15.66 DtN recovery."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_v1566_dynamic_dtn_recovery import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    exact_round_cap_residue,
    v1566_current_c2_recovery_classification,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_V1566_DYNAMIC_DTN_RECOVERY.json"
INPUTS = (
    A / "BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO.json",
    ROOT / "artifacts/BHSM_aether_round_cap_maxwell_dtn_v15_65.json",
    ROOT / "artifacts/BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json",
    ROOT / "artifacts/BHSM_aether_unified_m5_m4_pushforward_v15_69.json",
    ROOT / "src/bhsm/interface/ae31_c2_v1566_dynamic_dtn_recovery.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    no_go, cap, full_gauge, unified = map(_load, INPUTS[:4])
    residue = exact_round_cap_residue(2)
    recovery = v1566_current_c2_recovery_classification()
    boundary = claim_boundary()
    validation = {
        "current_route_no_go_reused": no_go["claim_boundary"][
            "CURRENT_AE31_RETAINED_ACTION_OUTER_CALDERON_COMPLETION_NO_GO_DERIVED"
        ],
        "static_round_cap_asset_reused": cap["claim_boundary"][
            "exact_static_weak_DtN_spectrum_derived"
        ],
        "full_gauge_ray_reused": full_gauge["claim_boundary"][
            "absolute_nonlocal_full_gauge_kernel_completed"
        ],
        "v1569_subtraction_still_open": not unified["claim_boundary"][
            "common_parent_regulator_and_subtraction_derived"
        ],
        "dynamic_derivative_verified": abs(
            residue["centered_difference_derivative"]
            + residue["minus_d_DtN_d_q_squared_exact"]
        ) < 2.0e-7,
        "round_cap_Maxwell_test_failed_honestly": (
            not residue["one_Lorentzian_Maxwell_residue"]
            and not recovery["v1566_supplies_missing_noncommon_current_C2_correction"]
        ),
        "double_counting_rejected": not recovery[
            "may_be_added_to_current_AE3_trace_without_double_counting"
        ],
        "downstream_not_overclaimed": (
            not boundary["CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_V1566_DYNAMIC_DTN_RECOVERY",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "lowest_mode_dynamic_residue": residue,
        "current_C2_recovery_classification": recovery,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("v15.66 dynamic DtN recovery failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
