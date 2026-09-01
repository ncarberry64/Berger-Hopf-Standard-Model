"""Materialize the current-C2 quark gauge LR channel ray."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_gauge_lr_channel_ray import (
    ACTION_VERSION,
    CLASSIFICATION,
    channel_direction_effect,
    claim_boundary,
    current_c2_transport_contract,
    exact_group_factor_ray,
    exact_remaining_owner,
    family_and_higgs_boundary,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_GAUGE_LR_CHANNEL_RAY.json"
INPUTS = (
    ROOT / "artifacts/BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json",
    A / "BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",
    A / "BHSM_AE31_C2_QUARK_HS_DIRECTION_NO_GO.json",
    A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json",
    A / "BHSM_AE31_C2_QUARK_SCALAR_ATTACHMENT_VARIATION.json",
    ROOT / "src/bhsm/interface/ae31_c2_quark_gauge_lr_channel_ray.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    historical, gauge, no_go, incidence, parity = map(_load, INPUTS[:5])
    ray = exact_group_factor_ray()
    transport = current_c2_transport_contract()
    direction = channel_direction_effect()
    family = family_and_higgs_boundary()
    remaining = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "historical_exact_group_factors_recovered": (
            historical["left_right_group_factors"]["pre_Fierz_attraction_weights"]["up"] == "7/5"
            and historical["left_right_group_factors"]["pre_Fierz_attraction_weights"]["down"] == "13/10"
            and ray["C_up_over_C_down"] == "14/13"
        ),
        "current_representation_support_reused": (
            incidence["claim_boundary"]["CURRENT_C2_QUARK_HIGGS_INCIDENCE_SUPPORT_TRANSPORTED_CONDITIONAL"]
            and parity["claim_boundary"]["CURRENT_C2_REQUIRED_ODD_DIRAC_ENDOMORPHISM_CLASS_DERIVED"]
        ),
        "relative_ray_does_not_override_Maxwell_mismatch": (
            not gauge["claim_boundary"]["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
            and not transport["Lorentzian_Maxwell_mismatch_overridden"]
            and not transport["nonlocal_static_kernel_relabelled_as_local_photon_exchange"]
        ),
        "gauge_ray_breaks_only_isolated_O2_degeneracy": (
            no_go["claim_boundary"]["CURRENT_C2_QUARK_HS_CHANNEL_DIRECTION_NULLITY"] == 1
            and direction["isolated_O2_quark_plane_degeneracy_broken"]
            and direction["largest_attraction_axis"] == "up"
            and not direction["mixed_up_down_eigendirection_selected"]
        ),
        "family_and_Yukawa_boundaries_preserved": (
            not family["family_hierarchy_generated"]
            and not family["single_intrinsic_Higgs_direction_selected"]
            and not family["historical_group_weights_relabelled_as_Yukawa_residues"]
            and not boundary["CURRENT_C2_UP_DOWN_RELATIVE_YUKAWA_RESIDUE_DERIVED"]
        ),
        "no_mass_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not remaining["quark_mass_fit_allowed"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_GAUGE_LR_CHANNEL_RAY",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "exact_group_factor_ray": ray,
        "current_c2_transport_contract": transport,
        "channel_direction_effect": direction,
        "family_and_higgs_boundary": family,
        "exact_remaining_owner": remaining,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark gauge LR channel ray failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
