"""Materialize the retained-action outer-Calderon no-go theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_outer_calderon_action_no_go import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    fermion_selector_configuration_space,
    gauge_outer_response_exhaustion,
    outer_calderon_no_go_theorem,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO.json"
INPUTS = (
    A / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    A / "BHSM_AE31_C2_FIXED_HISTORY_STATE_NONUNIQUENESS.json",
    A / "BHSM_AE31_C2_CALDERON_PRINCIPAL_SYMBOL.json",
    A / "BHSM_AE3_C2_TWO_SIDED_CALDERON_REFLECTION_NO_GO.json",
    A / "BHSM_AE3_C2_MAXWELL_COMMON_SHIFT_NO_GO.json",
    ROOT / "src/bhsm/interface/ae31_c2_outer_calderon_action_no_go.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    reset, state, symbol, reflected, common = map(_load, INPUTS[:5])
    fermion = fermion_selector_configuration_space()
    gauge = gauge_outer_response_exhaustion()
    theorem = outer_calderon_no_go_theorem()
    boundary = claim_boundary()
    validation = {
        "zero_surface_action_reused": (
            reset["action_definition"]["independent_normal_matter_boundary_action"]
            == "S_Sigma_F_AE2=0"
        ),
        "state_nonuniqueness_reused": (
            state["claim_boundary"]["CURRENT_C2_FIXED_HISTORY_PURE_HADAMARD_STATE_NONUNIQUENESS_DERIVED"]
            and fermion["continuum_preserves_reset_and_family_data"]
        ),
        "fixed_local_symbol_reused": (
            symbol["claim_boundary"]["CURRENT_C2_SPINOR_HADAMARD_CALDERON_PRINCIPAL_SYMBOL_DERIVED"]
            and fermion["continuum_shares_fixed_local_symbol"]
        ),
        "gauge_no_gos_reused": (
            not reflected["claim_boundary"]["Lorentzian_Maxwell_residue_derived"]
            and common["claim_boundary"]["CURRENT_C2_COMMON_COVARIANT_F2_SHIFT_NO_GO_DERIVED"]
            and gauge["retained_coefficient_free_local_and_reflected_routes_exhausted"]
        ),
        "scope_is_retained_route_only": (
            not gauge["all_possible_global_or_microscopic_extensions_excluded"]
            and not theorem["BHSM_as_a_whole_refuted"]
        ),
        "downstream_not_overclaimed": (
            not boundary["CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED"]
            and not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "fermion_selector_configuration_space": fermion,
        "gauge_outer_response_exhaustion": gauge,
        "outer_Calderon_no_go_theorem": theorem,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 retained-action outer-Calderon no-go failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
