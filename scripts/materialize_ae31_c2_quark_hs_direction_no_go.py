"""Materialize the AE3.1 quark HS channel-direction no-go."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_hs_direction_no_go import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    exact_channel_selector,
    family_tensor_pushforward_witness,
    historical_four_channel_trace_reuse,
    kinetic_normalization_nullity_theorem,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_HS_DIRECTION_NO_GO.json"
INPUTS = (
    A / "BHSM_AE31_C2_QUARK_PARENT_THIRD_VARIATION.json",
    A / "BHSM_AE31_C2_QUARK_YUKAWA_NORMALIZATION_NO_GO.json",
    A / "BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json",
    A / "BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json",
    ROOT / "artifacts/BHSM_aether_hs_channel_normalization_v16_02.json",
    ROOT / "src/bhsm/interface/ae31_c2_quark_hs_direction_no_go.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    third, normalization, hs, transport, historical = map(_load, INPUTS[:5])
    nullity = kinetic_normalization_nullity_theorem()
    trace = historical_four_channel_trace_reuse()
    family = family_tensor_pushforward_witness()
    selector = exact_channel_selector()
    boundary = claim_boundary()
    historical_channels = historical["HS_channel_normalization"]
    validation = {
        "parent_third_variation_gate_reused": (
            third["claim_boundary"][
                "CURRENT_AE31_UP_DOWN_INTRINSIC_HIGGS_THIRD_VARIATIONS_EVALUATED"
            ]
            and not third["claim_boundary"][
                "CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED"
            ]
        ),
        "one_channel_direction_survives_kinetic_normalization": (
            nullity["constraint_Jacobian_rank"] == 1
            and nullity["channel_direction_nullity"] == 1
            and abs(nullity["gradient_dot_tangent"]) < 1.0e-14
            and nullity["witness_relative_residues_differ"]
        ),
        "historical_multiplicity_reused_without_residue_promotion": (
            historical_channels["pairing_multiplicity_matrix"] == "D=diag(9,9,3,3)"
            and not historical_channels["physical_direction_selected"]
            and trace["quark_plane_quadratic_symmetry_when_no_other_terms_are_present"]
            == "O(2)"
            and not trace["historical_numeric_Z_pair_promoted_to_current_C2"]
        ),
        "family_tensoring_preserves_angle_ambiguity": (
            transport["claim_boundary"][
                "frozen_internal_Hopf_response_operator_attached_to_current_C2"
            ]
            and family["all_attachment_commutators_zero"]
            and family["within_sector_shapes_identical"]
            and family["cross_sector_ratio_changes"]
            and not family["family_tensoring_selects_channel_angle"]
        ),
        "current_HS_vertex_still_lacks_dynamical_selector": (
            hs["claim_boundary"]["current_C2_third_LR_HS_vertex_retained"]
            and not hs["claim_boundary"]["current_C2_dynamical_HS_kernel_derived"]
            and not hs["claim_boundary"]["current_C2_broken_LR_saddle_derived"]
        ),
        "previous_two_scalar_normalization_no_go_preserved": (
            normalization["normalization_nonidentifiability_theorem"][
                "normalization_nullity"
            ]
            == 2
        ),
        "exact_selector_is_full_channel_operator_and_unfitted": (
            "H_uu" in selector["minimum_block"]
            and not selector["diagonal_kinetic_trace_alone_sufficient"]
            and not selector["equal_components_may_be_assumed"]
            and not selector["quark_mass_fit_allowed"]
        ),
        "no_relative_residue_pole_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_UP_DOWN_RELATIVE_YUKAWA_RESIDUE_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_HS_DIRECTION_NO_GO",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "kinetic_normalization_nullity_theorem": nullity,
        "historical_four_channel_trace_reuse": trace,
        "family_tensor_pushforward_witness": family,
        "exact_channel_selector": selector,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark HS direction no-go failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
