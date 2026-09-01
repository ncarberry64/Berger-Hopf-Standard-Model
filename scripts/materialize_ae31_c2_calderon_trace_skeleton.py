"""Materialize the current-C2 gauge--spinor--ghost trace skeleton."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_calderon_trace_skeleton import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    exact_remaining_owner,
    physical_outer_calderon_contract,
    reset_transmission_complex,
    transmission_is_not_outer_calderon,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_CALDERON_TRACE_SKELETON.json"
INPUTS = (
    A / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    A / "BHSM_AE3_C2_TWO_SIDED_CALDERON_REFLECTION_NO_GO.json",
    A / "BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json",
    A / "BHSM_AE31_C2_FIXED_HISTORY_STATE_NONUNIQUENESS.json",
    A / "BHSM_AE31_C2_SCALAR_UV_HESSIAN_FACTORIZATION.json",
    A / "BHSM_AE3_C2_MAXWELL_COMMON_SHIFT_NO_GO.json",
    ROOT / "src/bhsm/interface/ae31_c2_calderon_trace_skeleton.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    reset, gauge, chiral, state, scalar, shift = map(_load, INPUTS[:6])
    skeleton = reset_transmission_complex()
    distinction = transmission_is_not_outer_calderon()
    contract = physical_outer_calderon_contract()
    owner = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "owned_reset_domain_reused": (
            reset["validation_passed"]
            and skeleton["all_Hermitian"]
            and skeleton["all_idempotent"]
            and skeleton["all_fix_the_reset_graph"]
        ),
        "gauge_reflection_failure_reused": (
            gauge["claim_boundary"]["Lorentzian_Maxwell_residue_derived"] is False
            and not distinction["reset_graph_repairs_gauge_residue"]
        ),
        "spinor_domain_and_nonselection_reused": (
            chiral["claim_boundary"]["current_C2_chiral_operator_domain_preserved_by_mass_block"]
            and state["claim_boundary"]["CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"] is False
            and distinction["reset_graph_preserves_Hadamard_covariance_continuum"]
        ),
        "one_shared_missing_owner_typed": (
            scalar["claim_boundary"]["CURRENT_C2_FINITE_ZERO_MOMENTUM_SCALAR_HESSIAN_DERIVED"] is False
            and shift["claim_boundary"]["CURRENT_C2_REQUIRED_NONCOMMON_GAUGE_RESIDUE_DIFFERENCE_DERIVED"]
            and contract["one_operator_would_close_three_dependencies"]
        ),
        "projector_not_fabricated": (
            not contract["operator_constructed_here"]
            and not contract["coefficient_or_state_inserted"]
            and not owner["reset_graph_may_be_relabelled_physical_projector"]
        ),
        "downstream_not_overclaimed": (
            not boundary["CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED"]
            and not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
            and not boundary["CURRENT_C2_FINITE_SCALAR_HESSIAN_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_CALDERON_TRACE_SKELETON",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "reset_transmission_complex": skeleton,
        "transmission_is_not_outer_Calderon": distinction,
        "physical_outer_Calderon_contract": contract,
        "exact_remaining_owner": owner,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 current-C2 Calderon trace skeleton failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
