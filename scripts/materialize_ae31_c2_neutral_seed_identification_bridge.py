"""Materialize the current-C2 historical neutral-seed identification bridge."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_neutral_seed_identification_bridge import (
    ACTION_VERSION,
    CLASSIFICATION,
    algebraic_mixing_screen,
    claim_boundary,
    historical_neutral_seed_spectrum,
    historical_shape_channel_decomposition,
    mode_coordinate_identification,
    provenance_and_owner_reconciliation,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_NEUTRAL_SEED_IDENTIFICATION_BRIDGE.json"
INPUTS = (
    ROOT / "artifacts/neutral_operator_no_fit_output_v1.json",
    ROOT / "artifacts/neutral_parameter_closure_or_obstruction_v1.json",
    ROOT / "artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json",
    A / "BHSM_AE31_C2_NEUTRAL_SEMIGROUP_RESPONSE_TRANSPORT.json",
    A / "BHSM_AE31_C2_CAPTURE_NEUTRINO_PROPAGATION_GATE.json",
    ROOT / "src/neutral_minimal_hessian.py",
    ROOT / "src/neutral_bridge_pmns_source.py",
    ROOT / "src/bhsm/interface/completion/pair_wake_neutrino_bvp_v14_55.py",
    ROOT / "src/bhsm/interface/ae31_c2_neutral_seed_identification_bridge.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    seed, obstruction, basis, response, capture = map(_load, INPUTS[:5])
    modes = mode_coordinate_identification()
    spectrum = historical_neutral_seed_spectrum()
    decomposition = historical_shape_channel_decomposition()
    mixing = algebraic_mixing_screen()
    owner = provenance_and_owner_reconciliation()
    boundary = claim_boundary()
    validation = {
        "historical_seed_reused": seed["neutral_boundary_operator"]
        == "CLOSED_AS_BOUNDARY_SEED",
        "historical_candidate_status_preserved": obstruction["status"]
        == "STRONGLY_SUPPORTED_CANDIDATE",
        "basis_scale_blocker_preserved": not basis["promotes_neutral_kernel"],
        "current_neutral_response_reused": response["validation_passed"],
        "capture_noncentrality_gate_reused": capture["validation_passed"],
        "mode_coordinate_bridge_exact": modes["slotwise_identification_exact"],
        "mode_costs_recovered": modes["mode_costs_recovered"],
        "indefinite_seed_detected": spectrum["one_negative_eigenvalue"],
        "v14_55_channel_decomposition_exact": decomposition[
            "exact_reconstruction"
        ],
        "v14_55_amplitudes_not_overclaimed": not decomposition[
            "channel_amplitudes_action_selected"
        ],
        "noncommuting_shape_detected": mixing["noncommuting_family_shape_present"],
        "source_condition_only_conditional": not mixing[
            "condition_is_sufficient_for_physical_oscillation"
        ],
        "action_ownership_not_overclaimed": not owner[
            "historical_seed_promoted_to_current_action_term"
        ],
        "particle_spectrum_not_rebuilt": not boundary["particle_spectrum_rebuilt"],
    }
    return {
        "artifact": "BHSM_AE31_C2_NEUTRAL_SEED_IDENTIFICATION_BRIDGE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "mode_coordinate_identification": modes,
        "historical_neutral_seed_spectrum": spectrum,
        "historical_shape_channel_decomposition": decomposition,
        "algebraic_mixing_screen": mixing,
        "provenance_and_owner_reconciliation": owner,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("neutral seed identification bridge failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
