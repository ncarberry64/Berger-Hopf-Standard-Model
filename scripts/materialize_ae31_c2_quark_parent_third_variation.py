"""Materialize the exact AE3.1 quark parent-third-variation evaluation."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_parent_third_variation import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    current_action_incidence_theorem,
    current_hs_vertex_separation,
    exact_next_owner,
    historical_residue_adjudication,
    maximal_eft_variation_theorem,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_PARENT_THIRD_VARIATION.json"
INPUTS = (
    A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json",
    A / "BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json",
    A / "BHSM_AE31_C2_QUARK_YUKAWA_NORMALIZATION_NO_GO.json",
    A / "BHSM_AE32_C2_EINSTEIN_CARTAN_LR_ACTION.json",
    ROOT / "artifacts/BHSM_aether_event_shell_joint_operator_v15_73.json",
    ROOT / "artifacts/BHSM_aether_proper_time_joint_pushforward_v15_91.json",
    ROOT / "artifacts/BHSM_aether_common_quantum_superdeterminant_v15_96.json",
    ROOT / "src/bhsm/interface/master_action/terms.py",
    ROOT / "src/bhsm/interface/master_action/coefficients.py",
    ROOT / "src/bhsm/interface/ae31_c2_quark_parent_third_variation.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    lepton, hs, no_go, ec, v1573, v1591, v1596 = map(_load, INPUTS[:7])
    current = current_action_incidence_theorem()
    eft = maximal_eft_variation_theorem()
    hs_separation = current_hs_vertex_separation()
    history = historical_residue_adjudication()
    next_owner = exact_next_owner()
    boundary = claim_boundary()
    validation = {
        "same_AE31_action_evaluated": (
            lepton["action_version"] == ACTION_VERSION
            and current["action_version"] == ACTION_VERSION
        ),
        "active_up_down_variations_zero_by_field_incidence": (
            current["up_zero_by_field_incidence"]
            and current["down_zero_by_field_incidence"]
            and not current["up_down_Yukawa_terms_added"]
        ),
        "maximal_EFT_variation_is_typed_input_recovery": (
            eft["only_T4_Yukawa_contributes"]
            and eft["coefficient_classification"] == "INDEPENDENT_THEORY_INPUT"
            and eft["variation_recovers_input_matrix"]
            and not eft["variation_derives_input_matrix"]
        ),
        "current_HS_vertex_not_misidentified": (
            hs["claim_boundary"]["current_C2_third_LR_HS_vertex_retained"]
            and not hs["claim_boundary"]["current_C2_dynamical_HS_kernel_derived"]
            and hs_separation["family_factor"] == "I3"
            and not hs_separation["intrinsic_H_or_H_tilde_derivative"]
            and not hs_separation["can_canonically_normalize_Y_u_or_Y_d"]
        ),
        "historical_event_shell_definition_not_promoted": (
            not v1573["v15_72_reclassification"]["claimed_actual_crossing"]
            and history["attachable_current_AE31_intrinsic_quark_residue_count"] == 0
        ),
        "proper_cycle_residue_is_family_central_and_Lorentz_mismatched": (
            v1591["proper_time_cycle_pushforward"]["family_Yukawa_matrix"]
            == "Y_proper*I3"
            and not v1591["claim_boundary"]["Lorentz_invariant_Maxwell_matching_derived"]
        ),
        "quantum_third_derivative_remains_unevaluated": (
            not v1596["claim_boundary"]["interacting_source_Hessian_discretized"]
            and not v1596["claim_boundary"]["coupled_quantum_event_saddle_solved"]
        ),
        "EC_and_previous_normalization_no_go_preserved": (
            not ec["claim_boundary"]["RETAINED_AE3_ZERO_MODE_IN_GLOBAL_EC_STATIONARY_ACTION_DOMAIN"]
            and no_go["normalization_nonidentifiability_theorem"]["normalization_nullity"] == 2
        ),
        "next_owner_is_specific_and_unfitted": (
            len(next_owner["required_derivatives"]) == 2
            and not next_owner["quark_mass_fit_allowed"]
            and not next_owner["independent_c_u_or_c_d_allowed"]
        ),
        "no_quark_pole_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_PARENT_THIRD_VARIATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "current_action_incidence_theorem": current,
        "maximal_eft_variation_theorem": eft,
        "current_hs_vertex_separation": hs_separation,
        "historical_residue_adjudication": history,
        "exact_next_owner": next_owner,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark parent third-variation evaluation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
