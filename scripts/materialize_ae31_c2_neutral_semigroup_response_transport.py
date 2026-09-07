"""Materialize the current-C2 neutral semigroup response transport."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_neutral_semigroup_response_transport import (
    ACTION_VERSION,
    CLASSIFICATION,
    charged_neutral_common_projector_test,
    claim_boundary,
    neutral_current_c2_attachment_certificate,
    neutral_internal_semigroup_shape,
    neutral_mode_ledger,
    propagation_owner_classification,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_NEUTRAL_SEMIGROUP_RESPONSE_TRANSPORT.json"
INPUTS = (
    ROOT / "artifacts/BHSM_aether_hybrid_flavor_spectrum_v15_54.json",
    A / "BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json",
    A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json",
    A / "BHSM_AE31_C2_CAPTURE_NEUTRINO_PROPAGATION_GATE.json",
    ROOT / "src/bhsm/interface/ae31_c2_neutral_semigroup_response_transport.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    historical, transport, lepton, capture = map(_load, INPUTS[:4])
    ledger = neutral_mode_ledger()
    shape = neutral_internal_semigroup_shape()
    common = charged_neutral_common_projector_test()
    attachment = neutral_current_c2_attachment_certificate()
    owner = propagation_owner_classification()
    boundary = claim_boundary()
    validation = {
        "historical_neutral_modes_reused": historical["validation_passed"],
        "current_C2_transport_reused": transport["validation_passed"],
        "charged_lepton_attachment_reused": lepton["validation_passed"],
        "capture_propagation_gate_reused": capture["validation_passed"],
        "left_right_neutral_ledgers_match": ledger["left_right_ledgers_match"],
        "neutral_response_noncentral": shape["family_noncentral"],
        "neutral_response_has_two_gaps": shape["two_nonzero_response_gaps"],
        "charged_neutral_common_projectors": common[
            "charged_neutral_commutator_norm"
        ] == 0.0,
        "tested_current_C2_attachment_commutators_zero": attachment[
            "all_tested_attachment_commutators_zero"
        ],
        "full_neutral_projector_not_overclaimed": not attachment[
            "physical_rank_three_neutral_subbundle_projector_derived"
        ],
        "canonical_source_does_not_convert": not common[
            "canonical_first_slot_source_converts"
        ],
        "basis_intertwiner_not_overclaimed": not common[
            "physical_weak_flavor_to_internal_slot_intertwiner_derived"
        ],
        "response_not_relabelled_propagation": (
            not shape["Lorentzian_unitary_propagation_operator"]
            and not owner["response_gaps_can_be_called_Delta_m_squared"]
        ),
        "particle_spectrum_not_rebuilt": not boundary["particle_spectrum_rebuilt"],
    }
    return {
        "artifact": "BHSM_AE31_C2_NEUTRAL_SEMIGROUP_RESPONSE_TRANSPORT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "neutral_mode_ledger": ledger,
        "neutral_internal_semigroup_shape": shape,
        "charged_neutral_common_projector_test": common,
        "neutral_current_C2_attachment_certificate": attachment,
        "propagation_owner_classification": owner,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("neutral semigroup response transport failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
