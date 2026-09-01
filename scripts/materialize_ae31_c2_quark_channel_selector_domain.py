"""Materialize the AE3.1 quark-channel selector domain theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_channel_selector_domain import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    classical_selector_domain,
    exact_dependency_order,
    quantum_selector_contract,
    selector_state_dependence_theorem,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_CHANNEL_SELECTOR_DOMAIN.json"
INPUTS = (
    A / "BHSM_AE31_C2_QUARK_HS_DIRECTION_NO_GO.json",
    A / "BHSM_AE31_C2_QUARK_PARENT_THIRD_VARIATION.json",
    A / "BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json",
    A / "BHSM_AE31_C2_FIXED_HISTORY_STATE_NONUNIQUENESS.json",
    A / "BHSM_AE31_C2_FERMION_HADAMARD_STATE_CLASS.json",
    ROOT / "artifacts/BHSM_aether_common_quantum_superdeterminant_v15_96.json",
    ROOT / "src/bhsm/interface/ae31_c2_quark_channel_selector_domain.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    direction, third, hs, nonunique, states, historical = map(_load, INPUTS[:6])
    classical = classical_selector_domain()
    state = selector_state_dependence_theorem()
    quantum = quantum_selector_contract()
    order = exact_dependency_order()
    boundary = claim_boundary()
    validation = {
        "direction_no_go_reused": (
            direction["claim_boundary"]["CURRENT_C2_QUARK_HS_CHANNEL_DIRECTION_NULLITY"] == 1
            and not direction["claim_boundary"]["CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED"]
        ),
        "intrinsic_undefined_separated_from_auxiliary_zero": (
            classical["intrinsic_quark_channel_Hessian_status"]
            == "UNDEFINED_ON_ACTIVE_FIELD_SPACE"
            and not classical["intrinsic_undefined_may_be_relabelled_zero"]
            and classical["reduced_probe_rank"] == 0
            and not classical["reduced_probe_is_complete_dynamical_HS_Hessian"]
        ),
        "third_variation_and_HS_boundaries_preserved": (
            not third["claim_boundary"]["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED"]
            and hs["claim_boundary"]["current_C2_third_LR_HS_vertex_retained"]
            and not hs["claim_boundary"]["current_C2_dynamical_HS_kernel_derived"]
        ),
        "state_dependence_counterexample_is_charge_compatible": (
            state["response_changes_within_same_Hadamard_class"]
            and max(state["finite_rank_rotated"]["vertex_charge_commutator_norms"]) == 0.0
            and not state["finite_rank_rotated"]["proxy_is_physical_BHSM_quark_Hessian"]
        ),
        "existing_state_nonuniqueness_reused": (
            nonunique["claim_boundary"][
                "CURRENT_C2_FIXED_HISTORY_PURE_HADAMARD_STATE_NONUNIQUENESS_DERIVED"
            ]
            and not states["claim_boundary"][
                "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"
            ]
        ),
        "historical_quantum_cycle_not_promoted": (
            not historical["claim_boundary"]["interacting_source_Hessian_discretized"]
            and not quantum["historical_periodic_superdeterminant_may_replace_current_domain"]
        ),
        "dependency_order_starts_with_missing_vertices": (
            order["first_missing_object"].endswith("V_u_V_d_Q_fg")
            and not order["physical_channel_diagonalization_ready"]
            and not order["quark_mass_fit_allowed"]
        ),
        "no_selector_pole_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_CHANNEL_SELECTOR_DOMAIN",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "classical_selector_domain": classical,
        "selector_state_dependence_theorem": state,
        "quantum_selector_contract": quantum,
        "exact_dependency_order": order,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark channel selector domain theorem failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
