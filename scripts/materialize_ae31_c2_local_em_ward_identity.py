"""Materialize the local current-C2 electromagnetic Ward identity."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_local_em_ward_identity import (
    ACTION_VERSION,
    CLASSIFICATION,
    charged_lepton_qem_ledger,
    local_em_claim_boundary,
    local_ward_identity_witness,
    pauli_transversality_witness,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_LOCAL_EM_WARD_IDENTITY.json"
INPUTS = (
    A / "BHSM_AE31_C2_NEUTRAL_CONNECTION_HESSIAN.json",
    A / "BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json",
    A / "BHSM_AE31_C2_CALDERON_PRINCIPAL_SYMBOL.json",
    ROOT / "src/bhsm/interface/ae31_c2_local_em_ward_identity.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    neutral, chiral, symbol = map(_load, INPUTS[:3])
    charge = charged_lepton_qem_ledger()
    ward = local_ward_identity_witness()
    pauli = pauli_transversality_witness()
    boundary = local_em_claim_boundary()
    validation = {
        "structural_Qem_current_reused": (
            neutral["claim_boundary"]["CURRENT_C2_STRUCTURAL_JQ_CURRENT_DERIVED"]
            and charge["current_C2_source_domain_attached"]
        ),
        "current_C2_chiral_mass_operator_reused": (
            chiral["claim_boundary"]["current_C2_first_order_charged_lepton_LR_operator_assembled"]
            and charge["mass_endomorphism_commutes_with_Qem"]
        ),
        "local_boundary_symbol_reused_without_photon_promotion": (
            symbol["claim_boundary"]["CURRENT_C2_RESET_EQUIVARIANT_FAMILY_PRESERVING_LOCAL_SYMBOL_DERIVED"]
            and not symbol["claim_boundary"]["CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED"]
        ),
        "Ward_identity_exact": (
            ward["Clifford_residual"] < 1.0e-12
            and ward["mass_charge_commutator_residual"] < 1.0e-12
            and ward["Ward_Takahashi_residual"] < 1.0e-12
        ),
        "Pauli_term_transverse": (
            pauli["antisymmetry_residual"] < 1.0e-12
            and pauli["q_sigma_q_residual"] < 1.0e-12
            and not pauli["Ward_identity_determines_F2"]
        ),
        "downstream_not_overclaimed": (
            not boundary["CURRENT_C2_CANONICALLY_NORMALIZED_PHOTON_VERTEX_DERIVED"]
            and not boundary["CURRENT_C2_RENORMALIZED_MUON_VERTEX_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_LOCAL_EM_WARD_IDENTITY",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "charged_lepton_Qem_ledger": charge,
        "local_Ward_identity": ward,
        "Pauli_transversality": pauli,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 current-C2 local EM Ward identity failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
