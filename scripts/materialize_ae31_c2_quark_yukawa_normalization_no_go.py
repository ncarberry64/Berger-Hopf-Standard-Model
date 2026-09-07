"""Materialize the AE3.1 quark Yukawa normalization no-go."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_yukawa_normalization_no_go import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    normalization_kernel_witness,
    normalization_nonidentifiability_theorem,
    provenance_and_exclusion_ledger,
)


A = ROOT / "artifacts/action_extension"
LEPTON_ACTION = A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json"
QUARK_RULES = A / "BHSM_AE3_C2_QUARK_RESPONSE_SUM_RULES.json"
CHARGED_CURRENT = A / "BHSM_AE31_C2_COEXACT_SU2L_CHARGED_CURRENT.json"
EC_ACTION = A / "BHSM_AE32_C2_EINSTEIN_CARTAN_LR_ACTION.json"
PARENT_BOUNDARY = ROOT / "theory/parent_action_boundary_derivation.json"
TARGET = A / "BHSM_AE31_C2_QUARK_YUKAWA_NORMALIZATION_NO_GO.json"
INPUTS = (
    LEPTON_ACTION,
    QUARK_RULES,
    CHARGED_CURRENT,
    EC_ACTION,
    PARENT_BOUNDARY,
    ROOT / "docs/research_packets/2026-08-03/BHSM_FINAL_PARENT_ACTION_LEPTON_MASS_COMPLETION_2026-08-03.md",
    ROOT / "docs/research_packets/2026-08-03/BHSM_QUARK_YUKAWA_PAIR_AND_CKM_INTERTWINER_2026-08-03.md",
    ROOT / "src/bhsm/interface/ae31_c2_quark_yukawa_normalization_no_go.py",
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
    lepton, quark_rules, charged_current, ec_action, parent_boundary = map(
        _load, INPUTS[:5]
    )
    theorem = normalization_nonidentifiability_theorem()
    witness = normalization_kernel_witness()
    provenance = provenance_and_exclusion_ledger()
    boundary = claim_boundary()
    parent_up_down = {
        row["sector"]: row
        for row in parent_boundary["reductions"]
        if row["sector"] in ("up", "down")
    }
    validation = {
        "same_AE31_action_and_lepton_normalization_owner_recovered": (
            lepton["action_version"] == ACTION_VERSION
            and lepton["claim_boundary"][
                "charged_lepton_M4_semigroup_coupling_action_owned_in_successor"
            ]
            and not lepton["claim_boundary"]["up_down_action_prefactors_derived"]
        ),
        "quark_response_shapes_and_sum_rules_reused": (
            quark_rules["claim_boundary"][
                "CURRENT_C2_UP_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED"
            ]
            and quark_rules["claim_boundary"][
                "CURRENT_C2_DOWN_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED"
            ]
            and not quark_rules["claim_boundary"][
                "CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_DERIVED"
            ]
        ),
        "two_dimensional_normalization_kernel_derived": (
            theorem["normalized_shape_Jacobian_rank"] == 0
            and theorem["normalization_nullity"] == 2
            and witness["up_shape_residual"] == 0.0
            and witness["down_shape_residual"] == 0.0
            and witness["cross_sector_ratio_changes"]
        ),
        "historical_boundary_scaffold_not_promoted": (
            parent_boundary["theorem_complete"] is False
            and all(not row["theorem_complete"] for row in parent_up_down.values())
            and not provenance["beta_kappa_can_be_relabelled_as_c_u_c_d"]
        ),
        "charged_current_and_virtual_dressing_boundary_preserved": (
            not charged_current["claim_boundary"][
                "up_down_absolute_Yukawa_prefactors_derived"
            ]
            and not charged_current["claim_boundary"][
                "middle_up_virtual_dressing_promoted"
            ]
            and not charged_current["claim_boundary"]["physical_CKM_matrix_derived"]
        ),
        "EC_route_not_repurposed_as_global_normalization": (
            not ec_action["claim_boundary"][
                "BHSM_AE32_FIRST_ORDER_EINSTEIN_CARTAN_COMPLETION_GLOBALLY_PROMOTED"
            ]
            and not ec_action["claim_boundary"][
                "RETAINED_AE3_ZERO_MODE_IN_GLOBAL_EC_STATIONARY_ACTION_DOMAIN"
            ]
            and not provenance[
                "EC_auxiliary_unit_vertex_supplies_global_quark_normalization"
            ]
        ),
        "exact_missing_parent_variations_named_without_fit": (
            "delta^3 S_parent" in theorem["exact_missing_variations"]["up"]
            and "delta^3 S_parent" in theorem["exact_missing_variations"]["down"]
            and not theorem["measured_quark_mass_can_select_the_normalizations"]
            and not provenance["independent_quark_normalization_inserted"]
        ),
        "no_quark_pole_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not boundary["particle_spectrum_rebuilt"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_YUKAWA_NORMALIZATION_NO_GO",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "normalization_nonidentifiability_theorem": theorem,
        "normalization_kernel_witness": witness,
        "provenance_and_exclusion_ledger": provenance,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark Yukawa normalization no-go failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
