"""Materialize the AE3.1 current-C2 neutral connection Hessian."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_neutral_connection_hessian import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    higgs_neutral_charge_ledger,
    lorentzian_photon_promotion_gate,
    neutral_connection_hessian,
    neutral_field_current_rotation,
)


A = ROOT / "artifacts"
AE31 = A / "action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json"
JY = A / "action_extension/BHSM_AE3_C2_COEXACT_HYPERCHARGE_SOURCE_JET.json"
J3 = A / "action_extension/BHSM_AE3_C2_COEXACT_SU2L_NEUTRAL_SOURCE_JET.json"
GAUGE = A / "action_extension/BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json"
REPRESENTATION = A / "BHSM_electromagnetic_surviving_generator_v6_3_0.json"
TARGET = A / "action_extension/BHSM_AE31_C2_NEUTRAL_CONNECTION_HESSIAN.json"
INPUTS = (
    AE31,
    JY,
    J3,
    GAUGE,
    REPRESENTATION,
    ROOT / "src/bhsm/interface/ae31_c2_neutral_connection_hessian.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    ae31, jy, j3, gauge, representation = map(_load, INPUTS[:5])
    charges = higgs_neutral_charge_ledger()
    hessian = neutral_connection_hessian()
    rotation = neutral_field_current_rotation()
    promotion = lorentzian_photon_promotion_gate()
    boundary = claim_boundary()
    validation = {
        "same_AE31_Higgs_action_and_no_measured_vev": (
            ae31["action_version"] == ACTION_VERSION
            and not ae31["conditional_higgs_saddle"]["measured_Higgs_VEV_used"]
        ),
        "Higgs_vacuum_is_Qem_neutral": charges["Q_em_on_vacuum"] == 0.0,
        "JY_and_J3_share_current_C2_domain": (
            jy["validation_passed"]
            and j3["validation_passed"]
            and j3["neutral_source_pair"]["both_sources_share_lowest_Weyl_coexact_C2_domain"]
        ),
        "neutral_Hessian_has_exactly_one_null_and_positive_broken_mode": (
            hessian["rank"] == 1
            and hessian["nullity"] == 1
            and hessian["Q_em_null_residual_exact"] == 0.0
            and hessian["Q_em_null_residual_floating"] < 2.0e-12
            and hessian["broken_curvature_positive"]
        ),
        "structural_Qem_matches_retained_representation": (
            charges["Q_em"] == "T3+Y_BH"
            and representation["generator"].startswith("Q_em=T_n+Y_BH")
        ),
        "fields_and_currents_rotate_together": (
            rotation["orthogonal_coordinate_transform"]
            and rotation["same_current_C2_source_domain"]
        ),
        "gauge_residue_mismatch_blocks_physical_photon": (
            gauge["claim_boundary"]["residue_outcome"]
            == "MISMATCH_RECORDED__NOT_RENORMALIZED"
            and not promotion["single_Lorentzian_Maxwell_residue_available"]
            and not boundary["CURRENT_C2_PHYSICAL_PHOTON_DERIVED"]
        ),
        "no_independent_gauge_or_mixing_input": (
            not charges["independent_g2_or_g1_inserted"]
            and not promotion["independent_ZA_g_gprime_alpha_or_mixing_angle_inserted"]
            and not boundary["independent_gauge_or_mixing_parameter_inserted"]
        ),
        "no_photon_muon_or_full_completion_overclaim": (
            not boundary["CURRENT_C2_PHOTON_POLE_AND_WARD_IDENTITY_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_NEUTRAL_CONNECTION_HESSIAN",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "higgs_neutral_charge_ledger": charges,
        "neutral_connection_Hessian": hessian,
        "neutral_field_current_rotation": rotation,
        "Lorentzian_photon_promotion_gate": promotion,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 neutral connection Hessian validation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
