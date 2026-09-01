"""Materialize the current-C2 gauge composite HS action."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_gauge_composite_hs_action import (
    ACTION_VERSION,
    CLASSIFICATION,
    action_owned_gauge_hs_contract,
    claim_boundary,
    current_c2_domain_and_trace_transport,
    exact_hs_completion_witness,
    exact_inverse_coefficients,
    intrinsic_higgs_mixing_boundary,
    odd_composite_endomorphism_attachment,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_GAUGE_COMPOSITE_HS_ACTION.json"
INPUTS = (
    ROOT / "artifacts/BHSM_aether_composite_higgs_channel_v15_64.json",
    A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json",
    A / "BHSM_AE31_C2_QUARK_SCALAR_ATTACHMENT_VARIATION.json",
    A / "BHSM_AE31_C2_QUARK_GAUGE_LR_CHANNEL_RAY.json",
    A / "BHSM_AE31_C2_LR_SUSCEPTIBILITY_FACTORIZATION.json",
    ROOT / "src/bhsm/interface/ae31_c2_gauge_composite_hs_action.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    historical, incidence, parity, gauge, susceptibility = map(_load, INPUTS[:5])
    witness = exact_hs_completion_witness()
    contract = action_owned_gauge_hs_contract()
    attachment = odd_composite_endomorphism_attachment()
    domain = current_c2_domain_and_trace_transport()
    mixing = intrinsic_higgs_mixing_boundary()
    inverse = exact_inverse_coefficients()
    boundary = claim_boundary()
    validation = {
        "historical_composite_representation_reused": (
            historical["claim_boundary"]["Higgs_representation_exists_as_derived_fermion_bilinear"]
            and incidence["claim_boundary"]["CURRENT_C2_QUARK_HIGGS_INCIDENCE_SUPPORT_TRANSPORTED_CONDITIONAL"]
        ),
        "exact_HS_rewrite_closes": (
            witness["completion_residual"] < 1.0e-12
            and witness["stationary_residual"] < 1.0e-12
            and not contract["new_continuous_coefficient"]
            and inverse["up_minus_down"] == "-5/182"
        ),
        "required_odd_class_realized_as_composite": (
            parity["claim_boundary"]["CURRENT_C2_REQUIRED_ODD_DIRAC_ENDOMORPHISM_CLASS_DERIVED"]
            and attachment["composite_HS_odd_endomorphism_action_owned_by_rewrite"]
            and not attachment["intrinsic_Higgs_odd_endomorphism_action_owned"]
        ),
        "current_C2_gauge_and_susceptibility_blocks_reused": (
            gauge["claim_boundary"]["CURRENT_C2_QUARK_GAUGE_LR_RELATIVE_CHANNEL_RAY_DERIVED"]
            and susceptibility["claim_boundary"]["CURRENT_C2_LR_HADAMARD_UV_POLE_FACTOR_DERIVED"]
            and domain["reset_generated_C2_domain_preserved"]
            and not domain["Einstein_Cartan_global_kernel_used"]
        ),
        "physical_Higgs_boundary_preserved": (
            not mixing["M_HS_action_derived"]
            and not mixing["auxiliary_field_is_physical_Higgs"]
            and not boundary["CURRENT_C2_CANONICAL_QUARK_YUKAWA_RESIDUES_DERIVED"]
            and not boundary["CURRENT_C2_COMPOSITE_GAP_DERIVED"]
        ),
        "no_mass_or_spectrum_fit": (
            not boundary["MEASURED_QUARK_MASS_USED"]
            and not boundary["particle_spectrum_rebuilt"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_GAUGE_COMPOSITE_HS_ACTION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "exact_hs_completion_witness": witness,
        "action_owned_gauge_hs_contract": contract,
        "odd_composite_endomorphism_attachment": attachment,
        "current_c2_domain_and_trace_transport": domain,
        "intrinsic_higgs_mixing_boundary": mixing,
        "exact_inverse_coefficients": inverse,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 current-C2 gauge composite HS action failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
