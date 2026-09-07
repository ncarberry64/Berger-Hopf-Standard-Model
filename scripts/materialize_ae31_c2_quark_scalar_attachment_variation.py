"""Materialize the quark scalar-attachment action-parity theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_scalar_attachment_variation import (
    ACTION_VERSION,
    CLASSIFICATION,
    chirality_parity_theorem,
    claim_boundary,
    current_action_internal_scalar_incidence,
    exact_remaining_owner,
    historical_parent_term_adjudication,
    required_odd_endomorphism_contract,
    scalar_only_variation_theorem,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_SCALAR_ATTACHMENT_VARIATION.json"
INPUTS = (
    A / "BHSM_AE31_C2_QUARK_PARENT_THIRD_VARIATION.json",
    A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json",
    A / "BHSM_AE31_C2_QUARK_HIGGS_CONTACT_CLOSURE.json",
    A / "BHSM_AE31_C2_QUARK_PROJECTOR_OVERLAP_BRIDGE.json",
    A / "BHSM_AE31_C2_UNIVERSAL_SCALAR_PROFILE_TRANSPORT.json",
    ROOT / "src/parent_internal_action.py",
    ROOT / "src/internal_action.py",
    ROOT / "src/bhsm_model.py",
    ROOT / "src/bhsm/interface/ae31_c2_quark_scalar_attachment_variation.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    third, incidence, contact, projector, profile = map(_load, INPUTS[:5])
    current = current_action_internal_scalar_incidence()
    parity = chirality_parity_theorem()
    scalar = scalar_only_variation_theorem()
    history = historical_parent_term_adjudication()
    odd = required_odd_endomorphism_contract()
    remaining = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "active_AE31_has_no_internal_Phi_coordinate": (
            current["action_version"] == ACTION_VERSION
            and not current["active_internal_Phi_field"]
            and not current["delta_S_AE31_over_delta_Phi_defined"]
            and third["current_action_incidence_theorem"]["up_zero_by_field_incidence"]
        ),
        "U1_connection_even_LR_support_odd": (
            parity["u1_chirality_commutator_norm"] == 0.0
            and parity["u1_left_right_block_norm"] == 0.0
            and parity["u1_right_left_block_norm"] == 0.0
            and parity["up_scalar_chirality_anticommutator_norm"] == 0.0
            and parity["down_scalar_chirality_anticommutator_norm"] == 0.0
            and not parity["even_U1_connection_variation_can_equal_odd_LR_scalar_vertex"]
        ),
        "profile_normalizes_but_does_not_generate_vertex": (
            profile["claim_boundary"]["CURRENT_C2_UNIVERSAL_SCALAR_PROFILE_PRESERVES_RADIAL_DOMAIN"]
            and scalar["kinetic_residue_conditionally_fixed"]
            and not scalar["profile_normalization_generates_Yukawa_vertex"]
            and set(scalar["mixed_third_variations"].values()) == {"0"}
        ),
        "historical_boundary_targets_not_relabelled": (
            not history["boundary_functional_full_action_variation_completed"]
            and not history["target_values_6_and_12_relabelled_as_Yukawa_residues"]
            and all(not row["can_own_c_u_c_d"] for row in history["rows"])
        ),
        "odd_endomorphism_reuses_existing_support_without_insertion": (
            odd["sample_grading_residual"] == 0.0
            and odd["existing_binary_supports_reused"]
            and incidence["quark_higgs_support_pencil"]["coefficients_in_support_pencil"]
            == "BINARY_INCIDENCE_ONLY"
            and not odd["coefficient_or_residue_inserted"]
            and not odd["object_promoted_into_AE31_action"]
        ),
        "downstream_projector_and_contact_assets_preserved": (
            projector["claim_boundary"]["CURRENT_C2_QUARK_PROJECTOR_OVERLAP_FUNCTIONAL_DERIVED"]
            and contact["claim_boundary"]["CURRENT_C2_QUARK_SQUARED_PENCIL_CONTACT_CLOSED_BY_FIRST_VERTICES"]
        ),
        "no_residue_pole_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_ODD_DIRAC_ENDOMORPHISM_ACTION_OWNED"]
            and not boundary["CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
            and not remaining["independent_yukawa_or_mass_fit_allowed"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_SCALAR_ATTACHMENT_VARIATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "current_action_internal_scalar_incidence": current,
        "chirality_parity_theorem": parity,
        "scalar_only_variation_theorem": scalar,
        "historical_parent_term_adjudication": history,
        "required_odd_endomorphism_contract": odd,
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
        raise SystemExit("AE3.1 quark scalar-attachment variation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
