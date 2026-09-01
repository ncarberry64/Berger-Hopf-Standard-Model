"""Materialize the AE3.2 current-C2 Einstein--Cartan LR action."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae32_c2_einstein_cartan_lr_action import (
    ACTION_VERSION,
    CLASSIFICATION,
    action_completion_contract,
    algebraic_hubbard_stratonovich_block,
    charged_bridge_separation_theorem,
    claim_boundary,
    contorsion_schur_complement,
    local_current_c2_lr_kernel,
    scalar_lr_channel_ledger,
)


A = ROOT / "artifacts"
AE31 = A / "action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json"
GREEN = A / "action_extension/BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json"
HS = A / "action_extension/BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json"
LOCALIZATION = A / "action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
V1575 = A / "BHSM_aether_einstein_cartan_joint_pushforward_v15_75.json"
V1576 = A / "BHSM_aether_cartan_shell_crossing_v15_76.json"
V1605 = A / "BHSM_aether_common_gauge_hs_pushforward_v16_05.json"
CHARGED = A / "charged_boundary_bridge_values_v1.json"
STIFFNESS = A / "BHSM_charged_action_stiffness_v1_7.json"
TARGET = A / "action_extension/BHSM_AE32_C2_EINSTEIN_CARTAN_LR_ACTION.json"
INPUTS = (
    AE31,
    GREEN,
    HS,
    LOCALIZATION,
    V1575,
    V1576,
    V1605,
    CHARGED,
    STIFFNESS,
    ROOT / "src/bhsm/interface/ae32_c2_einstein_cartan_lr_action.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    ae31, green, hs, localization, v1575, v1576, v1605, charged, stiffness = map(
        _load, INPUTS[:9]
    )
    completion = action_completion_contract()
    schur = contorsion_schur_complement()
    sample = local_current_c2_lr_kernel(np.asarray((-0.49, -0.25, 0.0, 0.25, 0.49)))
    channels = scalar_lr_channel_ledger()
    auxiliary = algebraic_hubbard_stratonovich_block()
    separation = charged_bridge_separation_theorem()
    boundary = claim_boundary()
    validation = {
        "predecessor_is_current_AE31_action": (
            ae31["action_version"] == completion["predecessor_action_version"]
            and green["action_version"] == completion["predecessor_action_version"]
        ),
        "first_order_lift_replaces_instead_of_double_counting": (
            completion["replacement_not_addition"]
            and completion["reduced_composition"].endswith("+Gamma_EC")
        ),
        "historical_completion_is_coefficient_free": (
            not v1575["first_order_parent_action"]["new_continuous_coefficient"]
            and not v1575["contorsion_Schur_complement"]["coefficient_inserted_by_hand"]
        ),
        "exact_historical_Clifford_coefficient_recovered": (
            schur["c_EC"] == v1576["Clifford_coefficient"]["c_EC"] == 0.75
        ),
        "current_AE3_localization_is_same_positive_weight": (
            localization["selected_candidate"] == "RECIPROCAL_JOIN_ETA_SIGMA_RESPONSE"
            and sample["positive"]
            and sample["reflection_even"]
        ),
        "all_24_historical_channel_pairings_attached": (
            channels["total_pairing_multiplicity"]
            == sum(v1605["common_M5_to_M4_pushforward"]["trace_ledger"]["HS_pairing_multiplicities"].values())
            == 24
        ),
        "current_reduced_vertex_preexisted_but_HS_kernel_was_open": (
            hs["claim_boundary"]["current_C2_third_LR_HS_vertex_retained"]
            and not hs["claim_boundary"]["current_C2_dynamical_HS_kernel_derived"]
        ),
        "algebraic_HS_block_is_not_overclaimed_as_propagating": (
            not auxiliary["HS_derivative_kinetic_term_present"]
            and not auxiliary["canonical_Yukawa_residue_derived"]
        ),
        "historical_charged_values_remain_non_action_normalizations": (
            charged["charged_boundary_values"] == "DERIVED_CONDITIONAL"
            and stiffness["action_normalization_status"]
            == "OPEN_MISSING_CHARGED_ACTION_NORMALIZATION"
            and not separation["beta_u_or_beta_d_promoted_to_Yukawa_prefactor"]
        ),
        "no_quark_mass_CKM_or_spectrum_overclaim": (
            not boundary["UP_DOWN_ACTION_YUKAWA_PREFACTORS_DERIVED"]
            and not boundary["QUARK_MASS_OPERATORS_DERIVED"]
            and not boundary["PHYSICAL_CKM_MATRIX_DERIVED"]
            and not boundary["particle_spectrum_rebuilt"]
        ),
    }
    return {
        "artifact": "BHSM_AE32_C2_EINSTEIN_CARTAN_LR_ACTION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "action_completion_contract": completion,
        "contorsion_Schur_complement": schur,
        "local_current_C2_LR_kernel_sample": sample,
        "scalar_LR_channel_ledger": channels,
        "algebraic_Hubbard_Stratonovich_block": auxiliary,
        "charged_bridge_separation_theorem": separation,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.2 Einstein--Cartan LR action validation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
